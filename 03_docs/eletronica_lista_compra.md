# MK I v0.2c: lista de compra da eletrônica (19/11/2026)

O que falta comprar para o braço funcionar, conferido contra o CAD da v0.2c. A auditoria (correntes, fonte, encaixe na base, riscos) está em `eletronica_auditoria.md`. Os parafusos estão em `mapa_parafusos_v02c.md`.

Preços em dólar, aproximados, pesquisados em 19/11/2026, **sem frete e sem impostos**. A compra é decisão sua.

## 1. Essencial (sem isto o braço não liga)

| # | Item | Qtd | Especificação (o que conferir no anúncio) | Por que | Preço aprox. (US$) |
|---|---|---|---|---|---|
| 1 | Servo Feetech **STS3215 12 V** | **6** | Versão **12 V, 30 kg·cm** (código C018, C044 ou C047; a Waveshare vende como "ST3215 12V 30kg"). **Não** comprar a C001 (7,4 V, 19 kg·cm): ela entra em proteção acima de 7,4 V. Vem com cabo 5264 de 3 vias de 15 cm, horn e parafusos. | Giro 1, ombro 2, cotovelo 1, punho 1, garra 1 (conferido no CAD: 4 bolsos de servo no braço, 1 berço na base, 1 na `garra_base`). | 26 a 31 cada em revendas (OpenELab, RobotShop). Na loja da Feetech no AliExpress costuma sair mais barato, mas não confirmei o preço de hoje. **6 × ~25 = ~150** |
| 2 | Waveshare **Bus Servo Adapter (A)** | 1 | Placa 42 × 33 mm, entrada 9 a 12,6 V por borne ou jack 5,5 × 2,1, USB-C para o notebook. Jumper na posição **B** (controle por USB). | Liga o notebook ao barramento dos servos (decisão fechada). | **5** (4,99 na Waveshare) |
| 3 | Fonte **12 V 10 A** (120 W) | 1 | Fonte de mesa fechada, tipo de notebook, com proteção de curto e sobrecorrente. Plugue P4 (5,5 × 2,1 ou 5,5 × 2,5: anote qual). Evite a "colmeia" aberta, que deixa os bornes da tomada expostos. | Pico realista de 6 a 8 A com o braço esticado e carregado; ver a seção 2 da auditoria. Uma de 5 A funciona, mas sem folga. | **15 a 20** |
| 4 | Botão de emergência **cogumelo 22 mm** | 1 | Trava ao apertar, solta girando. Pelo menos **1 contato NF**. Profundidade abaixo do painel **≤ 48 mm**. Aceitar painel de **6 a 6,5 mm** (confira a espessura máxima no anúncio, já que a tampa é de acrílico de 6 a 6,35 mm). | Corta os +12 V dos servos fisicamente (decisão fechada). | **4 a 8** |
| 5 | Jack DC fêmea de painel | 1 | Mesmo tamanho do plugue da fonte (5,5 × 2,1 ou 5,5 × 2,5), **≥ 5 A**, rosca para furo de **11 a 12 mm** (o furo da carcaça é de 12 mm). | Entrada dos 12 V no painel traseiro. | **1 a 2** |
| 6 | Porta-fusível em linha 5 × 20 mm + fusíveis **T6,3 A (lentos)** | 1 + 5 | Fusível de vidro de ação lenta. | Protege a fiação contra curto. Ver a seção 2. | **3 a 4** |
| 7 | Conector de alavanca **Wago 221-413** (3 vias) | 4 | Ou equivalente para fio de 0,2 a 4 mm². | Junção do +12 V depois do e-stop e do GND comum (2 usados, 2 de reserva). | **4 a 6** |
| 8 | Fio **18 AWG** (0,75 a 1 mm²) de silicone, vermelho e preto | 1 m de cada | Cabo flexível. | Caminho da potência: jack → fusível → e-stop → relé → Waveshare. | **4 a 6** |
| 9 | Cabo de servo **5264 de 3 vias, "mesmo sentido"** | 2 × 20 cm, 3 × 30 cm, 2 × 40 cm | Pino 1 de um lado ligado ao pino 1 do outro (**não** pode ser "sentido invertido": troca GND com 12 V e queima o servo). | O cabo de 15 cm que vem com o servo não alcança 3 dos 6 trechos. Ver a seção 4.3 da auditoria. | **5 a 8** (7 cabos) |
| 10 | Fita dupla-face de espuma (tipo VHB) | 1 rolo | 1 mm de espessura. | Fixa a Waveshare (furos de 2,5 mm, sem M3), o relé e os Wagos no fundo da base. Assim não precisa de parafuso fora do M3 nem de mudar o CAD. | **3 a 5** |

**Subtotal essencial: ~US$ 195 a 225** (com os servos a ~US$ 25).

## 2. Depende do que você já tem

| # | Item | Qtd | Quando comprar | Preço aprox. (US$) |
|---|---|---|---|---|
| 11 | Módulo relé 5 V de 1 canal (com transistor, diodo e bornes, contatos 10 A / 30 V DC) | 1 | Se o relé do seu kit for o componente solto (cubo azul SRD-05VDC-SL-C sem placa). Se já for módulo com bornes, pule. Plano B sem comprar: montar o driver com o transistor PN2222 e o diodo 1N4007 do kit numa plaquinha. | **2 a 3** |
| 12 | Cabo USB-A → USB-C de dados, 1,5 a 2 m | 1 | Se não tiver um sobrando (a Waveshare não traz cabo). O cabo USB-B do Arduino vem no kit. | **4 a 6** |
| 13 | Horn extra para STS3215 (25T, 4 furos M3) | 2 a 3 | O CAD usa **8 horns**: giro 1, ombro 2 (só os de fora), cotovelo 2, punho 2, garra 1. Se o anúncio disser que cada servo traz 1 horn, faltam 2 (lado de trás do cotovelo e do punho); compre 3, com 1 de reserva. Confira também se o lado de trás do servo aceita o horn (o eixo "passivo"). | **2 a 3 cada** |
| 14 | Multímetro simples | 1 | Se não tiver nem puder usar o do laboratório. Sem ele não dá para testar o e-stop nem a pinagem dos cabos (fase 1 do checklist). | **10 a 15** |
| 15 | Termorretrátil sortido | 1 kit | Se não tiver. | **2 a 4** |

## 3. Recomendado, opcional

| # | Item | Qtd | Por que | Preço aprox. (US$) |
|---|---|---|---|---|
| 16 | 1 STS3215 12 V de reserva | 1 | O ombro duplo e os testes de bancada são onde se queima servo. Com reserva, o projeto não para esperando a importação. | **~25** |

## 4. Não comprar

| Item | Motivo |
|---|---|
| Conversor 12 → 5 V | Perdeu a função (alimentava os dedos da v0.1). O Arduino e o relé usam os 5 V do USB do notebook, e a Waveshare tira a lógica do USB. O lugar dele na base fica vazio. **A decisão é sua (erro A11)**; esta é a minha recomendação. |
| Microservos MG90S, mola, cavilha 3/4", mastro | Saíram do projeto na v0.2b. |
| Segunda Waveshare | Uma controla até 253 servos. |

## 5. Já tem no kit Elegoo UNO R3 (não comprar)

Arduino UNO + cabo USB, relé 5 V, resistores de **10 kΩ e 5,1 kΩ** (divisor para ler os 12 V), botões (botão PARAR de software), transistor PN2222 e diodo 1N4007 (driver do relé, se precisar), jumpers Dupont, HC-SR04 (para depois). A webcam USB você já tem. Não usamos o módulo de alimentação de protoboard nem a bateria de 9 V do kit.

## 6. Mecânica (fora do orçamento de eletrônica, para fechar o pedido)

| Item | Qtd | Preço aprox. (US$) |
|---|---|---|
| Rolamento lazy susan de 4" (102 mm, furo de 63 mm) | 1 | 3 a 6 |
| Grampo C de 3" a 4" | 2 | 6 a 12 o par |
| Parafusos M3, insertos, porcas, arruelas | ver `mapa_parafusos_v02c.md` | 8 a 12 |

## 7. Total e orçamento

| Cenário | US$ (sem frete e impostos) |
|---|---|
| Essencial, servos a ~US$ 18 (se o AliExpress estiver nessa faixa) | ~150 |
| Essencial, servos a ~US$ 25 | ~205 |
| Essencial + itens da seção 2 + servo de reserva | ~260 a 290 |

**Cabe no orçamento de US$ 100 a 300 antes de frete e impostos.** Pode estourar os US$ 300 se os servos saírem pelo preço de revenda (~US$ 30) e você somar tudo da seção 2 e mais o servo de reserva.

**Se a compra for importada para o Brasil:** pelo que achei hoje (fontes de notícia, não o texto da Receita), compras de pessoa física de até US$ 50 por remessa em loja do Remessa Conforme estão com imposto de importação zero desde maio de 2026, mas pagam ICMS de 17 a 20% (calculado "por dentro", ~21 a 25% a mais). Acima de US$ 50, o imposto de importação é de 60% menos US$ 30, mais ICMS; algumas fontes falam em redução para 30%. Os 6 servos juntos passam de US$ 50, então o imposto pesa. Confira a regra no site da Receita e compare com lojas nacionais antes de fechar.

Fontes: [Feetech STS3215 12 V na RobotShop](https://www.robotshop.com/products/feetech-12v-30kgcm-magnetic-encoding-servo-sts3215), [STS3215-C018 na OpenELab](https://openelab.com/products/feetech-sts3215-c018-servo-12v), [datasheet do STS3215 (Core Electronics)](https://core-electronics.com.au/attachments/uploads/sts3215-smart-servo-datasheet-translated.pdf), [Waveshare Bus Servo Adapter (A), wiki](https://docs.waveshare.com/Bus_Servo_Adapter_A), [Waveshare Bus Servo Adapter (A), loja](https://www.waveshare.com/bus-servo-adapter-a.htm), [Forbes Brasil sobre a taxa das blusinhas (set/2026)](https://forbes.com.br/geral/2026/09/taxa-das-blusinhas-veja-como-ficam-as-compras-internacionais/), [Contmatic: isenção até US$ 50](https://simplifique.contmatic.com.br/blogs/taxa-das-blusinhas-isencao-compras-ate-50-dolares-2026).
