# MK I v0.2c: auditoria da eletrônica (19/11/2026)

Conferência elétrica e física da eletrônica contra o projeto: correntes, fonte, fusível, ligação, encaixe na base, cabos e os riscos abertos da consolidação. A lista de compra está em `eletronica_lista_compra.md`.

**Resultado:** a eletrônica fecha. Os 6 servos, a fonte e o e-stop funcionam juntos com folga. Achei **1 conflito físico** (o plugue USB do Arduino não passa pela janela traseira da base) e **3 pontos de atenção** (cabos curtos, corrente na corrente de servos, espessura do painel do e-stop). Todos têm solução. Só a da janela USB mexe no CAD, e ela espera o seu OK.

## 1. Confirmação contra o CAD

| Item | No CAD / decisão | Conferido |
|---|---|---|
| Quantidade de servos | Giro 1 (berço da base), ombro 2 (`SH_OFF` = ±19,25), cotovelo 1, punho 1, garra 1 | **6 × STS3215 12 V** (README e `montagem_b/manifest.json` com 5 servos de junta + o da `garra_base`) |
| Tamanho do servo | `SV_L, SV_W, SV_H = 45,2 × 24,7 × 35`, `SV_MASS = 55` | Igual ao datasheet (45,2 × 24,7 × 35 mm, 55 g) ✓ |
| Horns | Garfos: 2 placas × 4 parafusos em ombro, cotovelo e punho | **8 horns** no total. Ver o item 13 da lista. |
| Conector do servo | `CABO_L = 8`, `CABO_A = 3` nas presilhas | 5264 de 3 vias: pino 1 GND, 2 Vcc, 3 sinal. Cabe na presilha. |
| ID e velocidade de fábrica | — | Todos saem com **ID 1** e 1 Mbps (ver o risco R2) |

## 2. Correntes, fonte e fusível

Base: datasheet do STS3215 12 V (corrente de travamento de 2,7 A a 30 kg·cm, ~0,15 A em movimento sem carga) e os torques da auditoria de carga de 18/11. A corrente cresce com o torque, então: **I ≈ 0,15 A + 0,09 A por kg·cm**.

| Servo | Torque de pior caso (esticado, garra nova) | Corrente parada segurando | Pico (aceleração) |
|---|---|---|---|
| Giro | ~0 (só atrito) | 0,2 A | 0,8 A |
| Ombro A + B | 17,1 kg·cm (8,6 cada se dividido 50/50; 12 + 5 se 70/30) | 0,95 A cada (até 1,2 A em um) | 2 × 1,8 A |
| Cotovelo | 8,4 kg·cm | 0,9 A | 1,8 A |
| Punho | 2,4 kg·cm | 0,4 A | 1,0 A |
| Garra | Apertando um objeto | 0,3 a 0,8 A | 1,0 A |
| **Total** | | **~2,5 A típico, ~4 A no pior caso parado** | **~6 a 8 A por décimos de segundo** |

O teórico, com os 6 servos travados ao mesmo tempo, seria 16 A, mas não acontece: cada servo corta o torque sozinho depois de 2 s acima de ~2 A (proteção de sobrecorrente) ou acima de 80% de travamento (proteção de sobrecarga).

- **Fonte 12 V 10 A:** cobre os picos de 6 a 8 A sem a tensão cair. Com 5 A também funciona (é o que se usa em braços com 6 STS3215), mas qualquer pico derruba a tensão, e nosso ombro é mais pesado. O STS3215 aceita de 4 a 14 V e a Waveshare de 9 a 12,6 V, então 12 V está dentro dos dois.
- **Fusível T6,3 A lento, logo depois do jack:** aguenta os picos de 6 a 8 A por alguns segundos e queima num curto. O fusível protege a fiação; a fonte já tem proteção própria.
- **Fiação de potência em 18 AWG** (aguenta 10 A): jack → fusível → e-stop → relé → Waveshare.
- **Jack de painel ≥ 5 A:** a média fica entre 2,5 e 4 A, e os picos são curtos.
- **Relé do kit (SRD-05VDC-SL-C):** contatos de 10 A a 30 V DC. Folgado.
- **Contato NF do e-stop:** corrente térmica típica de 10 A. A 12 V e poucos ampères, cortar não faz arco relevante.

## 3. Diagrama de ligação

```
 Tomada ── Fonte 12 V 10 A ══ plugue P4 ══► JACK DC (painel traseiro)
                                              │ +12 V (18 AWG vermelho)
                                              ▼
                                   FUSÍVEL T6,3 A (em linha)
                                              ▼
                                   E-STOP, contato NF (em série)
                                              ▼
                                  [Wago A: +12 V depois do e-stop]
                                     │                 │
                                     │                 └── 10 kΩ ──┬── A0 do Arduino (lê se o e-stop está solto)
                                     ▼                             5,1 kΩ
                           RELÉ COM ──► NA                          │
                           (bobina: Arduino D7)                     GND
                                     │
                                     ▼  +12 V
                     WAVESHARE (A), borne +   ── barramento 5264 ──►
                                                 [1 giro] ─30cm─► [2 ombro A] ─15cm─► [3 ombro B]
                                                 ─40cm─► [4 cotovelo] ─30cm─► [5 punho] ─20cm─► [6 garra]

 Jack − (18 AWG preto) ──► [Wago B: GND] ──► Waveshare borne −
                                         └─► GND do Arduino (e o pé do divisor)

 Notebook USB ──► Waveshare USB-C (dados; jumper em B)
 Notebook USB ──► Arduino USB-B (dados + 5 V; o 5 V do Arduino alimenta o módulo do relé)
 Notebook USB ──► webcam (direto no notebook, não em hub)
```

O que a ligação garante:
1. **O e-stop corta os 12 V por hardware**, sem passar pelo Arduino nem pelo notebook. Com o software travado, ele continua funcionando.
2. **Fail-safe:** o relé usa o contato NA, então só passa os 12 V com a bobina ligada. Se o Arduino reinicia ou o USB cai, os servos desligam. Ao ligar o notebook, os servos só recebem energia depois que o software está pronto, o que evita o "pulo ao ligar".
3. **O divisor 10 k / 5,1 k** leva 4,0 V ao A0 com 12 V (4,7 V com 14 V: seguro para o Arduino). Assim o Arduino sabe que o e-stop foi apertado e mantém o relé aberto até o notebook rearmar.
4. **GND comum** entre fonte, Waveshare e Arduino. O USB do notebook já liga os GNDs; o fio no Wago B deixa isso explícito e evita leitura errada no A0.
5. O notebook precisa de **3 portas USB** livres (Waveshare, Arduino e webcam).

## 4. Encaixe físico na base

Rodado com a carcaça real (`parts.base_shell()`) e as medidas dos módulos a comprar. Script: `03_docs/auditoria/eletronica_encaixe.py`. Imagem: `04_imagens/eletronica_encaixe_v02c.png`. Espaço interno: 173,6 × 153,6 mm, 51,8 mm de altura até a tampa.

| Módulo | Medida usada | Resultado |
|---|---|---|
| Arduino UNO | 68,6 × 53,4 (oficial) + jumpers | Cabe; colunas já impressas na carcaça ✓ |
| **Plugue USB-B do Arduino** | Capa de 16 × 11,5 (estimada) | **Não passa.** A janela traseira está em z 19 a 33 e y 40 a 62; o conector do UNO fica em z 10,8 a 21,7 e y 49,8 a 61,8. Bate 8,5 mm embaixo e 1,8 mm do lado. Como o conector fica a só 4,4 mm da parede, não dá para plugar por dentro. Ver 4.1. |
| Waveshare (A) | 42 × 33 × 18,5 (oficial) | Cabe ✓ Fixar com fita VHB, porque os furos são de 2,5 mm e o projeto é todo em M3. Virar o USB-C para −X (lado do centro). |
| Módulo relé | 50 × 26 × 19 (estimado) | Cabe ✓ (lugar previsto) |
| Porta-fusível | ~60 × 12 × 14 (estimado) | Cabe ✓ "deitado" por cima do relé, preso no fio |
| 2 × Wago 221-413 | 18,6 × 13,1 × 8,2 cada (oficial) | Cabe ✓ (lugar dos "bornes") |
| Jack DC | Furo de 12 mm, ~22 mm de corpo | Cabe ✓ |
| Bloco do e-stop | 33 × 33 × 48 (estimado) | Cabe: sobram 3,8 mm até o fundo e só **0,3 mm até a parede da frente**. Na hora de montar, gire o bloco para o lado mais largo ficar em X. |
| Conversor 12→5 V | — | Não vai (lugar fica vazio) |

### 4.1 Conflito da janela USB: duas saídas

- **A (recomendada, muda o CAD):** aumentar a janela traseira de `y 40–62, z 19–33` para `y 42–66, z 8–34` em `base_shell()`. O plugue passa com folga de 2,2 a 5,8 mm, e o cabo USB-C da Waveshare passa junto. Muda só a `base_shell`: preciso exportar o STL de novo e refatiar o **lote 4** (ainda não impresso). Não muda nenhuma outra peça nem decisão.
- **B (sem mexer no CAD):** levantar o UNO com 4 espaçadores M3 macho-fêmea de 10 mm, o que alinha a altura (folga de 1 a 1,5 mm), e lixar ~2 mm do lado da janela depois de imprimir. Fica justo.

**Resolvido em 19/11 com a opção A** (aprovada): janela agora em y 42–66, z 8–34; `base_shell.stl` e lote 4 atualizados. Antigos em `99_arquivo/janela_usb_19nov/`.

### 4.2 E-stop na tampa de acrílico

Botões de 22 mm costumam aceitar painel de 1 a 6 mm. A tampa no CAD tem 6,35 mm (`ACRYLIC`); a chapa da universidade pode ter 6,0. Se o botão não rosquear, a solução é gravar no laser um rebaixo de ~1 mm por baixo da tampa, em volta do furo. Isso muda só o arquivo de laser, não a impressão. Decida com o botão na mão.

### 4.3 Comprimento dos cabos dos servos

| Trecho | Caminho | Precisa | Cabo |
|---|---|---|---|
| Waveshare → giro | Dentro da base | ~10 cm | 15 cm do servo ✓ |
| Giro → ombro A | Sobe pelo furo de 62 mm da tampa e pela torre, com folga para os ±135° de giro | ~20 cm | **30 cm** |
| Ombro A → ombro B | Lado a lado | ~6 cm | 15 cm do servo ✓ |
| Ombro B → cotovelo | 160 mm + laço de 50 mm + saídas | ~25 a 28 cm | **40 cm** |
| Cotovelo → punho | 150 mm + laço de 50 mm | ~23 cm | **30 cm** |
| Punho → garra | Laço de 50 mm + caixa da garra | ~13 a 15 cm | **20 cm** (o de 15 cm fica no limite) |

Antes de montar, confira cada extensão com o multímetro no modo de continuidade: pino 1 com pino 1 (fio preto, GND).

### 4.4 Corrente pela corrente de servos (atenção)

Toda a corrente do braço passa pelos conectores 5264 do giro e do ombro A. São ~2,5 A no uso normal e até ~4 A parado no pior caso, e o conector é especificado para ~3 A. Braços com 6 STS3215 em corrente usam assim sem problema, porque o pior caso é curto. Mitigação: o software limita o tempo com o braço esticado e carregado. No teste da fase 7, toque nos conectores depois de 5 minutos de uso: se esquentarem, a correção é um par de fios de 18 AWG levando +12 V e GND direto até o ombro.

## 5. Riscos abertos e como mitigar

### R1. Os 2 servos do ombro brigando

Os dois seguram o mesmo garfo. Se a posição de um estiver alguns graus diferente da do outro, cada um empurra contra o outro, esquenta e entra em proteção. O estriado de 25 dentes só deixa acertar de 14,4° em 14,4°, então o ajuste fino tem que ser no software.

1. **Antes de montar o garfo:** ligue os dois, mande os dois para 2048 (centro) com torque ligado e só então encaixe os horns nas placas (fase 5 do checklist).
2. **Sentido:** o ombro B gira espelhado. Use o bit de sentido do servo, se o firmware tiver (o datasheet diz "sentido de rotação configurável"), ou faça no software: `alvo_B = 4095 − alvo_A + offset_B`.
3. **Offset fino:** com o braço numa pose parada, leia a carga (`Present_Load`) dos dois. Ajuste `offset_B` alguns passos por vez até as cargas ficarem parecidas e com o mesmo sinal. Cargas altas e com sinal oposto querem dizer que estão brigando. Grave o offset na EEPROM.
4. **Comando junto:** sempre um único pacote SYNC WRITE para os IDs 2 e 3, nunca dois comandos separados.
5. **Vigia no software:** se a diferença de carga entre os dois passar de um limite por mais de 1 s, ou a temperatura de um passar de 55 °C, o braço para e avisa.

### R2. Todos os servos saem com ID 1

1. Ligue **um servo por vez** na Waveshare (só ele no barramento).
2. Grave o ID com o script de configuração (vou escrever em Python com o SDK da Feetech; o programa FD da Feetech para Windows também serve): **1 giro, 2 ombro A, 3 ombro B, 4 cotovelo, 5 punho, 6 garra**.
3. Grave no mesmo passo: limites de ângulo (ombro −27,5° a +120°, cotovelo até −105°, giro ±135°), limite de torque, proteção de sobrecorrente e o bit de sentido do ombro B. Depois trave a EEPROM.
4. Etiquete cada servo com o número (fita crepe) antes de tirar do barramento.

### R3. O braço cai quando o e-stop corta os 12 V

Sem energia, o servo não segura. A redução de 1:345 freia um pouco, mas o ombro com 12 a 17 kg·cm provavelmente desce. Isso é esperado num e-stop que corta energia (parada "categoria 0"). A queda é de ~0,5 kg, então o objetivo é que ela aconteça em lugar seguro, não evitá-la.

1. **Duas paradas diferentes:** "PARAR" (voz, tecla ou o botão do kit ligado ao Arduino) congela o braço **com torque**, segurando no lugar. O e-stop é o último recurso e corta tudo.
2. **Pose de descanso:** sempre que parado, o braço vai para uma pose de pouco torque (braço em pé e antebraço dobrado sobre a base). O pior caso de queda vira poucos centímetros.
3. **Teste de queda** na fase 2 (bancada), com 1 servo e um peso conhecido, para ver quanto o servo desce sem energia.
4. **Proteção do próprio servo:** deixe a proteção de sobrecarga do ombro com tempo mais longo (ex.: 3 a 4 s) para ele não soltar sozinho num pico de esforço.

### R4. "Pulo" ao religar

Já coberto pelo relé (seção 3, item 2). A sequência de rearme no software: relé liga → espera 300 ms → ping nos 6 IDs → lê as posições atuais → grava alvo = posição atual → liga o torque com velocidade baixa → só então aceita comandos.

### R5. Conversor 12→5 V sem função

Não comprar (seção 4 da lista). A decisão é sua.

## 6. O que só dá para fechar com as peças na mão

Já estava no checklist da consolidação (fases 1 e 2); a eletrônica acrescenta:
- Medir com régua a Waveshare, o relé, o e-stop (profundidade e espessura do painel) e o jack, e atualizar as caixas em `eletronica_encaixe.py`.
- Conferir quantos horns vêm com cada servo e se o lado de trás aceita horn.
- Conferir o comprimento real do cabo do servo (o datasheet diz 15 cm).
- Testar o e-stop sem servo nenhum: apertar e conferir no multímetro que os 12 V somem no borne da Waveshare.

Fontes: [datasheet do STS3215 (Core Electronics)](https://core-electronics.com.au/attachments/uploads/sts3215-smart-servo-datasheet-translated.pdf), [STS3215 12 V na RobotShop](https://www.robotshop.com/products/feetech-12v-30kgcm-magnetic-encoding-servo-sts3215), [Waveshare Bus Servo Adapter (A), wiki](https://docs.waveshare.com/Bus_Servo_Adapter_A), auditoria de carga de 18/11 (`03_docs/auditoria/`).

## 7. Próximos passos (para estarmos na mesma página)

### Agora: você
1. ~~Responder se posso alargar a janela USB da base~~ (feito: opção A). Abrir o lote 4 no PrusaSlicer e exportar o G-code de novo.
2. Confirmar se fica sem o conversor 12→5 V.
3. Revisar a lista e fazer o pedido. Confira que os servos são **12 V** (C018/C044/C047) e quantos horns vêm com cada um.
4. Imprimir o lote 1 (cupom + armaduras laranja) e testar o cupom seguindo `cupom_teste_folgas.md`.
5. Pendências antigas: fazer o merge do PR #2 no GitHub e salvar os documentos do Fusion.

### Agora: eu
1. ~~Lista de compra, auditoria e script de encaixe~~ (feito).
2. ~~Alterar a janela em `base_shell()`, exportar o STL e atualizar o lote 4~~ (feito em 19/11).
3. ~~Escrever o script de configuração dos servos e o sketch do Arduino~~ (feito em 19/11, em `06_software/`; ainda não testados com hardware).

### Depois do cupom: você
1. Me mandar os números que venceram (inserto, passante, piloto e bolso do servo).
2. Se nada mudar: imprimir os lotes 2, 3, 5 e o 4 (este só depois da decisão da janela), mais as pontas de TPU (lote 6). Cortar a tampa e a placa no laser.
3. Quando a eletrônica chegar: medir os módulos com régua, testar o e-stop sem servos e começar a fase 1 (um servo na bancada).

### Depois do cupom: eu
1. Se alguma folga mudar: ajustar `params.py`, gerar os STL de novo, refatiar os lotes 2 a 5 e subir por PR.
2. Se nada mudar: liberar a impressão e fechar a v0.2c (tag).
3. Guiar a fase 1: rodar o script de IDs com um servo por vez, conferir os cabos e atualizar `eletronica_encaixe.py` com as medidas reais.
