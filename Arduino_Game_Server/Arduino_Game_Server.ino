
#define MACADDRESS 0x00,0x01,0x02,0x03,0x04,0x05
#define MYIPADDR 192,168,1,6
#define MYIPMASK 255,255,255,0
#define MYDNS 192,168,1,1
#define MYGW 192,168,1,1
#define LISTENPORT 1000
#define UARTBAUD 115200


#include <UIPEthernet.h>

EthernetServer server = EthernetServer(LISTENPORT);

void setup() {
  uint8_t mac[6] = {MACADDRESS};
  uint8_t myIP[4] = {MYIPADDR};
  uint8_t myMASK[4] = {MYIPMASK};
  uint8_t myDNS[4] = {MYDNS};
  uint8_t myGW[4] = {MYGW};

  Serial.begin(9600);
  Serial.println("OK! Booting stuff");
  
  //  Ethernet.begin(mac,myIP);
  Ethernet.begin(mac,myIP,myDNS,myGW,myMASK);

  Serial.println("Ok, m-am conectat la retea");

  server.begin();
}

union float_decoder_type{
  float f;
  unsigned char b[4];
};

#define MAX_PLAYERS 15

EthernetClient clients[MAX_PLAYERS];
int currentClientID = 0;

// Given a client socket, it must return ID if the client
// is among the clients array
// or -1 otherwise
char getClientId(EthernetClient client){
  for ( int i = 0; i < MAX_PLAYERS; i++ ){
     if ( clients[i] == client ){
       Serial.println("Am gasit clientul!");
       return i;
     }
  }
  return -1;
}

void send_packet7(EthernetClient sock, char ID, float posx, float posy) {
  sock.write(7);
  sock.write(ID);
  union float_decoder_type u;
  // encodare din float in bytes
  u.f = posx;
  sock.write(u.b[3]);
  sock.write(u.b[2]);
  sock.write(u.b[1]);
  sock.write(u.b[0]);
  u.f = posy;
  sock.write(u.b[3]);
  sock.write(u.b[2]);
  sock.write(u.b[1]);
  sock.write(u.b[0]);
}

void send_packet6(EthernetClient sock, char ID) {
  sock.write(6);
  sock.write(ID);
}

void send_packet10(EthernetClient sock, char ID) {
  sock.write(10);
  sock.write(ID);
}

void send_packet9(EthernetClient sock, char ID) {
  sock.write(9);
  sock.write(ID);
}

void loop() {
  size_t size;

  // server.accept() accepta conexiuni daca exista in Pending...
  EthernetClient newClient = server.accept();
  // newClient este echivalent cu 0 in if daca nu e nicio conexiune de acceptat
  if (newClient) {

    char clientID = getClientId(newClient);
    // daca nu e deja inregistrat in array-ul de clients
    if ( clientID == -1 ){
      clients[currentClientID] = newClient;
      clientID = currentClientID;
      currentClientID++;
      Serial.println("Am inregistrat un client!");

      for (int i = 0; i < MAX_PLAYERS; i++) {
        if (clients[i] && clients[i].connected() && i != clientID) {
          // se trimite catre toti ceilalti ca s-a conectat userul nou care are ID-ul clientID
          send_packet6(clients[i], clientID);
          // se trimite clientului nou ca erau deja conectati ceilalti useri cu ID-ul i
          send_packet6(clients[clientID], i);
        }
      }
    }
  }

    // primirea datelor de la toti clientii conectati, pe rand
    for ( int clientID = 0; clientID < MAX_PLAYERS; clientID++ ){
      EthernetClient client = clients[clientID];
      if ( client ){
        while((size = client.available()) > 0)
        {
          Serial.print("Am primit niste date! De la clientul : ");
          Serial.println((int)clientID);
          
          uint8_t* msg = (uint8_t*)malloc(size+1);
          memset(msg, 0, size+1);
          size = client.read(msg,size);

          switch(msg[0]){
            case 8:
              Serial.println("Am primit un color command!");
              for (int i = 0; i < MAX_PLAYERS; i++) {
                if (clients[i] && clients[i].connected() && i != clientID) {
                  send_packet9(clients[i], clientID);
                }
              }
              break;
            case 5:{
              Serial.println("Am primit un pachet de pozitie!");
              Serial.println(size);
              union float_decoder_type u;
              // decodam x
              u.b[3] = msg[1];
              u.b[2] = msg[2];
              u.b[1] = msg[3];
              u.b[0] = msg[4];
              Serial.println(u.f);
              float posx = u.f;
              // decodam y
              u.b[3] = msg[5];
              u.b[2] = msg[6];
              u.b[1] = msg[7];
              u.b[0] = msg[8];
              Serial.println(u.f);

              for (int i = 0; i < MAX_PLAYERS; i++) {
                if (clients[i] && clients[i].connected() && i != clientID) {
                  send_packet7(clients[i], clientID, posx, u.f);
                }
              }
              
              break;
            }
          }

          /*
          for ( int i = 0; i < size; i++ ){
            Serial.write((char)msg[i]);
          }
          */
          free(msg);
        }
      //client.stop();
      }
    }

    // stop any clients which disconnect
    for (byte i = 0; i < MAX_PLAYERS; i++) {
    // daca e un socket pus la clients[i] si acela deconectat, ii dam stop
    if (clients[i] && !clients[i].connected()) {
      clients[i].stop();
      Serial.print("User exited. id : ");
      Serial.println(i);
      for (int j = 0; j < MAX_PLAYERS; j++) {
        if (clients[j] && clients[j].connected() && j != i) {
          // i = ID user deconectat
          // j = ID-urile celorlalti jucatori
          send_packet10(clients[j], i);
        }
      }
    }
  }

}
