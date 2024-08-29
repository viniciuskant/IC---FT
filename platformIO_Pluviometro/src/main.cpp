/*
 * platformIO_Pluviometro - Um exemplo de projeto C
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
#include <PubSubClient.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h> //Suporte para a biblioteca Adafruit_BMP280
#include <Adafruit_BMP280.h>
#include "DHT.h"

#define ledWiFi 14
#define ledMQTT 12
#define DHT22_PIN 2
#define pinHall 13
#define MSG_BUFFER_SIZE 200
#define topic_BUFFER_SIZE 100

WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_BMP280 bmp;
DHT dht22(DHT22_PIN, DHT22);

// Há vários wifis que posso tentar conectar e, assim, facilitar a conexão
const char *ssid0 = ""; 
const char *password0 = "";
const char *ssid1 = ""; 
const char *password1 = "";
const char *ssid2 = "";
const char *password2 = "";
const char *mqtt_server = ""; // servirdor embarcacoes.ic.unicamp.br
unsigned long lastMsg = 0;

char msg[MSG_BUFFER_SIZE];

char topicDHT22Temperatura[topic_BUFFER_SIZE] = "ic/pluviometro/DHT22/Temperatura(°C)";
char topicDHT22Huminade[topic_BUFFER_SIZE] = "ic/pluviometro/DHT22/Humidade(%)";


char topicBMPTemperatura[topic_BUFFER_SIZE] = "ic/pluviometro/BMP280/Temperatura(°C)";
char topicBMPPressao[topic_BUFFER_SIZE] = "ic/pluviometro/BMP280/Pressao(Pa)";
char topicBMPAltitude[topic_BUFFER_SIZE] = "ic/pluviometro/BMP280/Altitude(m)";

char topicOscilacoes[topic_BUFFER_SIZE] = "ic/pluviometro/Oscilacoes/Por Ciclo";
char topicOscilacoesParciais[topic_BUFFER_SIZE] = "ic/pluviometro/Oscilacoes/Parciais";
char topicPrecipitacao[topic_BUFFER_SIZE] = "ic/pluviometro/Chuva/TaxaPrecipitacao(mmh)";
char topicMilimetros[topic_BUFFER_SIZE] = "ic/pluviometro/Chuva/Milimetros(mm)";

char topicHallMedicao[topic_BUFFER_SIZE] = "ic/pluviometro/Hall/Medicao";
char topicHallStatus[topic_BUFFER_SIZE] = "ic/pluviometro/Hall/Status";
char topicStatus[topic_BUFFER_SIZE] = "ic/pluviometro/Status";

unsigned long now = 1000000;

int statusWifi = 0;

int testBMP280()
{
  return bmp.begin(0x76);
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
    String clientId = "espKant-Pluviometro";
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
      // Wait 5 seconds before retrying
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

void customPrint(char topic[], char msg[])
{
  client.publish(topic, msg);
  snprintf(msg, MSG_BUFFER_SIZE, "%s %s\n", topic, msg);
  Serial.println(msg);
}

void readDHT2(float *humi, float *tempC)
{
  *humi = dht22.readHumidity();
  *tempC = dht22.readTemperature();
}

void printDHT22()
{

  // Imprimi todos os dados do sensor BMP280

  float humi, tempC;
  humi = dht22.readHumidity();
  tempC = dht22.readTemperature();

  if (isnan(humi) || isnan(tempC)){
    snprintf(msg, MSG_BUFFER_SIZE, "0");
    customPrint(topicDHT22Temperatura, msg);
    snprintf(msg, MSG_BUFFER_SIZE, "0");
    customPrint(topicDHT22Huminade, msg);
  }
  else{
    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", tempC);
    customPrint(topicDHT22Temperatura, msg);
    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", humi);
    customPrint(topicDHT22Huminade, msg);

  }
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
  else{
    float tempC, pressao, altitude;
    // readBMP280(&tempC, &pressao, &altitude);
    tempC += bmp.readTemperature();
    pressao += bmp.readPressure();
    altitude += bmp.readAltitude();

    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", tempC);
    client.publish(topicBMPTemperatura, msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", pressao);
    client.publish(topicBMPPressao, msg);

    snprintf(msg, MSG_BUFFER_SIZE, "%.2f", altitude);
    client.publish(topicBMPAltitude, msg);
  }
}


void printOscilacoes(int *n, int temp)
{
  /*
    Input:
      n = variavel responsável com contar e retornar o número de oscilações
      temp = variavel responsável por indicar quanto tempo dura a medição

    Output:
      1 se a medição ocorreu bem, 0 se ocorreu erro
  */

  snprintf(msg, MSG_BUFFER_SIZE, "PrintOscilações\n"); // Imprimo o estado atual
  customPrint(topicStatus, msg);

  *n = 0;
  int status = 0;
  float ini = millis(), time = 0, porcentagem;
  while ((millis() - ini) < temp)
  {
    int erro = 0;
    if (millis() - time > 5000)
    {
      /*Envio uma mensagem a cada 5s para o senvidor, para saber que o esquipamento ta funcionando*/
      time = millis();
      porcentagem = ((time - ini) * 100) / temp;
      if (status == 0)
      {
        Serial.print(".");
        snprintf(msg, MSG_BUFFER_SIZE, "Lendo oscilacoes.      %.2f %%\n", porcentagem);
        client.publish(topicStatus, msg);
        status++;
      }
      else if (status == 1)
      {
        Serial.print(".");
        snprintf(msg, MSG_BUFFER_SIZE, "Lendo oscilacoes..     %.2f %%\n", porcentagem);
        client.publish(topicStatus, msg);
        status++;
      }
      else
      {
        Serial.print(".");
        snprintf(msg, MSG_BUFFER_SIZE, "Lendo oscilacoes...    %.2f %%\n", porcentagem);
        client.publish(topicStatus, msg);
        status = 0;
      }
    }
    if ((digitalRead(pinHall)) == 0)
    {
      (*n) += 1;
      snprintf(msg, MSG_BUFFER_SIZE, "%d", *n);
      customPrint(topicOscilacoesParciais, msg);
      delay(150);
    }
    delay(150);
  }
  snprintf(msg, MSG_BUFFER_SIZE, "%d", *n);
  customPrint(topicOscilacoes, msg);
}

void printMilimetros(int nOscilacoes, int temp)
{
  /*
    Imprimi quantos milimetros de chiva foram medidos no intervalo "temp"
  */

  float volumeOscilacao = 2.4; // cm3 ou ml
  float areaCaptacao = 63.24;  // cm2

  float milimetros = (nOscilacoes * volumeOscilacao * 10) / areaCaptacao;
  snprintf(msg, MSG_BUFFER_SIZE, "%.2f", milimetros);
  customPrint(topicMilimetros, msg);

  float precipitacao = (milimetros * 3600) / temp;
  snprintf(msg, MSG_BUFFER_SIZE, "%.2f", precipitacao);
  customPrint(topicPrecipitacao, msg);
}

void setup()
{
  Serial.begin(115200);

  dht22.begin(); // initialize the DHT22 sensor
  pinMode(ledWiFi, OUTPUT);
  pinMode(ledMQTT, OUTPUT);
  pinMode(pinHall, INPUT);


  configWiFi();

  client.setServer(mqtt_server, 8883); // Configuro a porta do servidor
  client.setCallback(callback);
}

void loop()
{
  int tempoMedida = 300000;   // Em ms, esse tempo controla o ciclo entre as medições
  int tempOscilacao = 295000; // Em ms, esse temmpo é o tempo que meço as oscilações

  int nOscilacao = 0;

  if (!client.connected())
  {
    reconnect();
  }

  client.loop();

  if (now - lastMsg > tempoMedida)
  {
    lastMsg = millis();
    snprintf(msg, MSG_BUFFER_SIZE, "0");
    customPrint(topicOscilacoesParciais, msg);
    printOscilacoes(&nOscilacao, tempOscilacao);
    printMilimetros(nOscilacao, tempOscilacao / 1000);
    printBMP280();
    printDHT22();
  }
  now = millis();
  snprintf(msg, MSG_BUFFER_SIZE, "Esperando...\n");
  customPrint(topicStatus, msg);
  delay(1000);
}