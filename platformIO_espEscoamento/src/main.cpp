/*
 * platformIO_espEscoamento - Um exemplo de projeto C
 * Copyright (C) 2024 Vinicius Patriarca Miranda Miguel

 * Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
 * sob os termos da Licença Pública Geral GNU como publicada pela Free Software
 * Foundation, tanto a versão 3 da Licença, como (a seu critério) qualquer versão posterior.

 * Este programa é distribuído na esperança de que seja útil,
 * mas SEM NENHUMA GARANTIA; sem mesmo a garantia implícita de
 * COMERCIABILIDADE ou ADEQUAÇÃO A UM DETERMINADO FIM. Veja a
 * Licença Pública Geral GNU para mais detalhes.

 * Você deve ter recebido uma cópia da Licença Pública Geral GNU
 * junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.
 */

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <Ultrasonic.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

#define ledWiFi 12
#define ledMQTT 14
#define triggerPin 15
#define echoPin 13
#define tempoMedida 1000 * 30
#define MSG_BUFFER_SIZE 100
#define topic_BUFFER_SIZE 50
#define numberEsp 1

Ultrasonic ultrasonic(triggerPin, echoPin);
WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_BMP280 bmp;

float alturaSensor;
float ultimaAltura = 0;
float raioGalao = 30; // raio em cm
float ultimoTempo = 0;
int status = 0;

unsigned long lastMsg = 0;
char msg[MSG_BUFFER_SIZE];
char topic[topic_BUFFER_SIZE];

char topicBMPTemperatura[topic_BUFFER_SIZE];
char topicBMPPressao[topic_BUFFER_SIZE];
char topicBMPAltitude[topic_BUFFER_SIZE];

char topicEscoamento[topic_BUFFER_SIZE];
char topicNivelAgua[topic_BUFFER_SIZE];
char topicVolume[topic_BUFFER_SIZE];
char topicDistancia[topic_BUFFER_SIZE];
char topicRaio[topic_BUFFER_SIZE];
char topicStatus[topic_BUFFER_SIZE];

int statusWifi = 0;

// Há vários wifis que posso tentar conectar e, assim, facilitar a conexão
const char *ssid0 = ""; 
const char *password0 = "";
const char *ssid1 = ""; 
const char *password1 = "";
const char *ssid2 = "";
const char *password2 = "";
const char *mqtt_server = ""; // servirdor embarcacoes.ic.unicamp.br

void customPrint(char topic[], char msg[])
{
  client.publish(topic, msg);
  snprintf(msg, MSG_BUFFER_SIZE, "%s %s\n", topic, msg);
  Serial.println(msg);
}

void configWiFi() // configurar para tentar conectar com diferentes redes
{
  while (WiFi.status() != WL_CONNECTED)
  {
    int lastTime = millis();
    Serial.println();
    Serial.print("Conectando a ");

    if (statusWifi == 0) // Uma máquina de estados para tentar conectar a diferentes redes
    {
      Serial.print(ssid0);
      WiFi.begin(ssid0, password0);
    }
    else if (statusWifi == 1)
    {
      Serial.print(ssid1);
      WiFi.begin(ssid1, password1);
    }
    else if (statusWifi == 2)
    {
      Serial.print(ssid2);
      WiFi.begin(ssid2, password2);
    }

    while (WiFi.status() != WL_CONNECTED)
    {
      digitalWrite(ledWiFi, 1); // led piscando enquanto tenta conectar
      delay(250);
      digitalWrite(ledWiFi, 0);
      delay(250);
      Serial.print("."); // imprime um ponto a cada 500ms, para saber que está tentando conectar

      if (((int)millis() - lastTime) > 10000) // a cada 5 segundos troco a rede que tento conectar
      {
        statusWifi++;
        if (statusWifi == 3)
          statusWifi = 0;
        break;
      }
    }
  }
  digitalWrite(ledWiFi, 1);
  Serial.println("");
  Serial.println("Conectado à rede Wi-Fi");
}

void callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect()
{
  digitalWrite(ledMQTT, 1);

  while (!client.connected())
  {
    while (WiFi.status() != WL_CONNECTED)
    {
      digitalWrite(ledMQTT, 0);
      configWiFi();
    }
    Serial.print("Attempting MQTT connection...");
    String clientId = "espKant-X";
    clientId[8] = numberEsp + 48;
    const char *userMqtt = "";
    const char *passwordMqtt = "";
    int statusLed = 0;

    if (client.connect(clientId.c_str(), userMqtt, passwordMqtt))
    {
      Serial.println("connected");
    }
    else
    {
      Serial.print("faistatusLed, rc=");
      Serial.print(client.state());
      Serial.println(" try again...");
      for (int i = 0; i < 20; i++)
      {
        statusLed = 1 - statusLed;
        digitalWrite(ledMQTT, statusLed);
        delay(250);
      }
    }
  }
  digitalWrite(ledMQTT, 1);
}

int testBMP280()
{
  return bmp.begin(0x76);
}

int readHCSR04()
{
  /* 
    Este código lê a distância do sensor ultrassônico e retorna a distância medida em centímetros
  */
  return ultrasonic.distanceRead();
}

void readBMP280(float *tempC, float *pressao, float *altitude)
{
  /*
    Realiza "limit" medições e retorna a média dessas medições
    O intuito é reduzir medições erradas.
  */
  int limit = 20;
  *tempC = 0;
  *pressao = 0;
  *altitude = 0;
  for (int i = 0; i < limit; i++)
  {
    *tempC += bmp.readTemperature();
    *pressao += bmp.readPressure();
    *altitude += bmp.readAltitude();
  }
  *tempC /= limit;
  *pressao /= limit;
  *altitude /= limit;
}

void printBMP280()
{
  // Imprimi todos os dados do sensor BMP280
  if (!testBMP280())
  {
    snprintf(msg, MSG_BUFFER_SIZE, "0");
    customPrint(topicBMPTemperatura, msg);
    snprintf(msg, MSG_BUFFER_SIZE, "0");
    customPrint(topicBMPPressao, msg);
    snprintf(msg, MSG_BUFFER_SIZE, "0");
    customPrint(topicBMPAltitude, msg);
  }
  else
  {
    float tempC, pressao, altitude;
    readBMP280(&tempC, &pressao, &altitude);

    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", tempC);
    client.publish(topicBMPTemperatura, msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", pressao);
    client.publish(topicBMPPressao, msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", altitude);
    client.publish(topicBMPAltitude, msg);
  }
}

void printHCSR04(float distancia)
{
  snprintf(msg, MSG_BUFFER_SIZE, "%.2f", alturaSensor - distancia);
  Serial.print(msg);
  client.publish(topicNivelAgua, msg);
}

void printEscoamento(float distancia)
{
  float atualAltura;

  atualAltura = alturaSensor - distancia;

  float fluxo = ((atualAltura - ultimaAltura) * 3.14 * raioGalao * raioGalao) / tempoMedida; // cm³ / s
  ultimaAltura = atualAltura;

  if (fluxo < 0)
    snprintf(msg, MSG_BUFFER_SIZE, "Esvaziando o galao.\n");
  else
    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", fluxo);
  Serial.print(msg);
  client.publish(topicEscoamento, msg);
}

void printVolume(float distancia)
{
  float atualAltura;

  atualAltura = alturaSensor - distancia;

  float volume = (atualAltura * 3.14 * raioGalao * raioGalao); // cm³

  if (volume < 0)
    snprintf(msg, MSG_BUFFER_SIZE, "Erro");
  else
    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", volume);
  Serial.print(msg);
  client.publish(topicVolume, msg);
}

void setup()
{
  pinMode(ledWiFi, OUTPUT);
  pinMode(ledMQTT, OUTPUT);
  snprintf(topic, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d", numberEsp);
  snprintf(topicRaio, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/raio(cm)", numberEsp);
  snprintf(topicEscoamento, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/Escoamento(cm3 por s)", numberEsp);
  snprintf(topicNivelAgua, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/NivelAgua(cm)", numberEsp);
  snprintf(topicVolume, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/Volume(cm3)", numberEsp);
  snprintf(topicBMPTemperatura, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/BMP280/Temperatura(°C)", numberEsp);
  snprintf(topicBMPPressao, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/BMP280/Pressao(Pa)", numberEsp);
  snprintf(topicBMPAltitude, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/BMP280/Altitude(m)", numberEsp);
  snprintf(topicDistancia, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/DistanciaAgua(1) (cm)", numberEsp);
  snprintf(topicRaio, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/RaioGalao", numberEsp);
  snprintf(topicStatus, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/Status", numberEsp);

  Serial.begin(9600);

  configWiFi();
  testBMP280();

  client.setServer(mqtt_server, 8883);
  client.setCallback(callback);
  alturaSensor = readHCSR04() + 0.3; // em cm
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
  snprintf(msg, MSG_BUFFER_SIZE, "%.2f", alturaSensor);
  Serial.print(msg);
  client.publish(topicDistancia, msg);
  snprintf(topicDistancia, topic_BUFFER_SIZE, "ic/escoamentoTelhado-%d/DistanciaAgua(cm)", numberEsp);

  snprintf(msg, MSG_BUFFER_SIZE, "%.2f", raioGalao);
  Serial.print(msg);
  client.publish(topicRaio, msg);
}

void loop()
{
  float ini = millis();
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
  unsigned long now = millis();
  if (now - lastMsg > tempoMedida)
  {
    lastMsg = now;
    float distancia = readHCSR04();
    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", distancia);
    Serial.print(msg);
    client.publish(topicDistancia, msg);

    printHCSR04(distancia);
    printVolume(distancia);
    printEscoamento(distancia);
    printBMP280();
    ini = millis();
  }
  else if (millis() - ultimoTempo > 5000)
  {
    /*Envio uma mensagem a cada 5s para o senvidor, para saber que o esquipamento ta funcionando*/
    ultimoTempo = millis();
    float porcentagem = ((now - lastMsg) * 100) / (tempoMedida);
    if (status == 0)
    {
      Serial.print(".");
      snprintf(msg, MSG_BUFFER_SIZE, "Aguardando proxima leitura.      %.2f %%\n", porcentagem);
      client.publish(topicStatus, msg);
      status++;
    }
    else if (status == 1)
    {
      Serial.print(".");
      snprintf(msg, MSG_BUFFER_SIZE, "Aguardando proxima leitura..     %.2f %%\n", porcentagem);
      client.publish(topicStatus, msg);
      status++;
    }
    else
    {
      Serial.print(".");
      snprintf(msg, MSG_BUFFER_SIZE, "Aguardando proxima leitura...    %.2f %%\n", porcentagem);
      client.publish(topicStatus, msg);
      status = 0;
    }
  }
}
