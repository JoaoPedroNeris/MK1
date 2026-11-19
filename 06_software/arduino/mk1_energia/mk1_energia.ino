// MK I v0.2c - controle de energia dos servos (Arduino UNO do kit Elegoo)
// AINDA NAO TESTADO COM HARDWARE (19/11/2026). Ligacao: 03_docs/eletronica_auditoria.md, secao 3.
//
// O e-stop corta os 12 V por hardware, antes deste circuito. Este sketch so:
//  - liga o rele (12 V para a Waveshare) quando o notebook manda "ARMAR" e o e-stop esta solto;
//  - desliga o rele na hora se os 12 V somem (e-stop apertado) e so religa com novo "ARMAR";
//  - avisa o notebook quando o botao PARAR e apertado (o notebook congela o braco COM torque).
//
// Serial 115200. Comandos do notebook (terminados em \n): ARMAR, DESARMAR, STATUS.
// Respostas: "OK ARMADO", "OK DESARMADO", "ERRO ESTOP", "EVENTO ESTOP", "EVENTO PARAR",
// e a cada 500 ms: "S armado=<0/1> v12=<volts> estop=<0/1>".

const uint8_t PINO_RELE   = 7;    // IN do modulo rele (ativo em ALTO; inverta RELE_LIGA se o seu for ativo em BAIXO)
const uint8_t PINO_PARAR  = 2;    // botao do kit entre D2 e GND
const uint8_t PINO_V12    = A0;   // divisor: +12 V (depois do e-stop) -- 10k -- A0 -- 5k1 -- GND
const uint8_t RELE_LIGA   = HIGH;
const uint8_t RELE_DESLIGA = (RELE_LIGA == HIGH) ? LOW : HIGH;

const float DIVISOR = (10.0 + 5.1) / 5.1;   // 2,96
const float V_MIN_OK = 10.0;               // abaixo disso: e-stop apertado ou fonte desligada

bool armado = false;
bool parar_antes = HIGH;
unsigned long t_status = 0;
String linha;

float le_v12() {
  long soma = 0;
  for (uint8_t i = 0; i < 8; i++) soma += analogRead(PINO_V12);
  return (soma / 8.0) * 5.0 / 1023.0 * DIVISOR;   // 5 V do USB: erro de uns 5%, suficiente aqui
}

void rele(bool liga) {
  digitalWrite(PINO_RELE, liga ? RELE_LIGA : RELE_DESLIGA);
  armado = liga;
}

void setup() {
  digitalWrite(PINO_RELE, RELE_DESLIGA);   // antes do pinMode, para nao dar pulso ao ligar
  pinMode(PINO_RELE, OUTPUT);
  pinMode(PINO_PARAR, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.println("MK1 energia pronto (DESARMADO)");
}

void comando(String c) {
  c.trim(); c.toUpperCase();
  if (c == "ARMAR") {
    if (le_v12() < V_MIN_OK) { Serial.println("ERRO ESTOP"); return; }
    rele(true);  Serial.println("OK ARMADO");
  } else if (c == "DESARMAR") {
    rele(false); Serial.println("OK DESARMADO");
  } else if (c == "STATUS") {
    t_status = 0;
  }
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { comando(linha); linha = ""; }
    else if (linha.length() < 32) linha += ch;
  }

  float v = le_v12();
  if (armado && v < V_MIN_OK) {        // e-stop apertado: rele abre e fica aberto
    rele(false);
    Serial.println("EVENTO ESTOP");
  }

  bool parar = digitalRead(PINO_PARAR);
  if (parar == LOW && parar_antes == HIGH) Serial.println("EVENTO PARAR");
  parar_antes = parar;

  if (millis() - t_status >= 500) {
    t_status = millis();
    Serial.print("S armado="); Serial.print(armado);
    Serial.print(" v12=");     Serial.print(v, 1);
    Serial.print(" estop=");   Serial.println(v < V_MIN_OK);
  }
  delay(10);
}
