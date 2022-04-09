# Projeto de Simulação - Algotrading
### Vinícius Matheus Morales
___
## Introdução
O estudo realizado nesse projeto tem como tema mesclar três indicadores técnicos para a tomada de decisão de compra ou venda de um determinado ativo.
___

## Metodologia
Os indicadores que serão utilizados para tal serão:
- Bollinger Bands https://en.wikipedia.org/wiki/Bollinger_Bands
- KST Oscillator https://en.wikipedia.org/wiki/KST_oscillator
- Parabolic SAR https://en.wikipedia.org/wiki/Parabolic_SAR

### Bollinger Bands
Calcula-se um range em torno da média móvel com base em uma quantidade *m* de desvios padrão da média de um período *n*.
> Upper band = avg(p, n) + m * std(p, n)

> Lower band = avg(p, n) - m * std(p, n)

Pode ser interpretado de diversas maneiras, tais como:
1. Comprar quando o preço tocar a banda inferior e vender quando tocar a banda superior.
2. Comprar quando o preço tocar a banda superior e vender quando tocar a banda inferior.
3. Comprar quando o preço tocar a banda inferior e zerar posição quando tocar a média móvel.
4. Utilizar um *m* baixo e um *n* rápido para atuar como *trend follower*.
5. etc.

Nesse projeto será usado como *trend follower*
___
### KST Oscillator
Primeiro calcula-se quatro taxas de variação suavizadas com tendo como base *X1*, *X2*, *X3* e *X4* dias anteriores.
> ROC1 = (Price/Price(X1) - 1) * 100

> ROC2 = (Price/Price(X2) - 1) * 100

> ROC3 = (Price/Price(X3) - 1) * 100

> ROC4 = (Price/Price(X4) - 1) * 100

Sendo *X1*, *X2*, *X3* e *X4* iguais à, respectivamente:
- 10, 15, 20, 30 (dias)
- 10, 13, 15, 20 (semanas)
- 9, 12, 18, 24 (meses)

Então suaviza as taxas de variação, respectivamente, seguindo padrões recomendados por Martin J Pring (criador do indicador) com base em médias móveis simples, nomeadas de *AVG1*, *AVG2*, *AVG3* e *AVG4*, com valores:
- 10, 10, 10, 15 (dias)
- 10, 13, 15, 20 (semanas)
- 6, 6, 6, 9 (meses)

Tendo também, como padrão, os pesos *W1*, *W2*, *W3* e *W4*, respectivamente:
> W1 = 1

> W2 = 2

> W3 = 3

> W4 = 4

Ficando então como fórmula final:
> KST = MOV(ROC1, AVG1) * W1 + MOV(ROC2, AVG2) * W2 + MOV(ROC3, AVG3) * W3 + MOV(ROC4, AVG4) * W4

Sendo que MOV(ROC, AVG) é a média móvel simples do período *AVG* de taxa de variação *ROC*

Por fim, se compara os cruzamentos com a média móvel simples de 9 dias, semanas ou meses.

A tomada de decisão se baseia em:
1. Comprar quando KST cruzar vindo por baixo da média móvel de 9 dias, semanas ou meses.
2. Vender quando KST cruzar vindo por cima da média móvel de 9 dias, semanas ou meses.
___
### Parabolic Stop And Reverse (PSAR)
Esse indicador é excelente para ser usado como stop loss ou stop gain, será com essa funcionalidade que ele será usado no projeto.

O cálculo dele é feito da seguinte forma:
$$ SAR(amanhã) = SAR(hoje) + AF(EP - SAR(hoje)) $$

Sendo AF e EP, respectivamente, Acceleration Factor e Extreme Point, ou seja, fator de aceleração e ponto extremo.

Porém existem dois casos, o PSAR em alta e o PSAR em queda, sendo diferenciado na equação como:

PSAR em alta:
> SAR(amanhã) = SAR(hoje) + AF(EP - SAR(hoje))

PSAR em queda:
> SAR(amanhã) = SAR(hoje) - AF(EP - SAR(hoje))
___
## Resultado esperado
Será utilizada a seguinte fórmula para determinar qual caminho seguir:
> signal = bb + 2*(kst + psar)

Ou seja, se o KST e o PSAR discordarem entre si, o mercado será considerado em tendência e a decisão será do Bollinger Bands.

Já se eles concordarem, o mercado será considerado oscilatório e a decisão será tomada por eles.

Vale ressaltar que as posições que podem ser tomadas são:
- 1 para entrar comprado
- -1 para entrar vendido
- 0 para não ter posição no momento

E também que:
> signal = 1 , signal > 0

> signal = -1 , signal < 0

> signal = 0 , signal = 0

Tendo então como conjunto:
> S = {[-1, 1] | S∈Z}

O *stop gain* e *stop loss* para o mercado em tendência será o próprio Bollinger Bands com um lag adicional de 4 dias, enquanto para o mercado oscilatório será o PSAR.
