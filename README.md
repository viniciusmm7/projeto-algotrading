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
- Zero Lag Exponential Moving Average https://en.wikipedia.org/wiki/Zero_lag_exponential_moving_average

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

Então 
___
## Resultado esperado
Ao mesclar esses indicadores é esperado que 
