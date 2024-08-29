
#ifndef WIFISTATE_H_
#define WIFISTATE_H_

#include <ESP8266WiFiType.h>
#include <user_interface.h>

struct WiFiState
{
    uint32_t crc;
    struct
    {
        station_config fwconfig;
        ip_info ip;
        ip_addr_t dns[2];
        ip_addr_t ntp[2];
        WiFiMode_t mode;
        uint8_t channel;
        bool persistent;
    } state;
};

#endif // WIFISTATE_H_
