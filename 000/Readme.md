## @000 Estressados A: Busca

![](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/000/cover.jpg)

[](toc)

- [Intro](#intro)
- [Draft](#draft)
- [Shell](#shell)
[](toc)

***
## Intro

- Na entrada de um evento de um experimento social, os participantes ganhavam uma pulseira especial que precisavam ficar utilizando.
- A pulseira informava, num pequeno visor, um número inteiro que representava o nível de stress daquele participante.
- O número 1 significava totalmente tranquilo e vai aumentando conforme o stress do participante aumentava até o valor máximo de infinito.
- Para fazer uma representação lógica de homens e mulheres em um vetor de inteiros, os números positivos representam os homens e os números negativos representam mulheres.
- Precisamos escrever os algorítmos que identifiquem informações importantes sobre os participantes da fila.

**Exemplos:** 

- `{}` equivale a uma fila vazia.
- `{-1, -50, -99}` equivale a uma mulher totalmente tranquila, uma mulher médio estressada e uma mulher extremamente estressada.
- `{80, 70, 90, -4}` equivale a três homens estressados e uma mulher tranquila. 


**Funções**:

- **in**: existe determinado valor na fila?
- **index_of**: qual posição aparece X na fila pela primeira vez?
- **find_if**: qual a posição do primeiro homem da fila?
- **min_element**: qual a posição do menor valor da lista?
- **find_min_if**: qual a posição do homem mais calmo?

***
## Draft

- [solver.cpp](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/000/.cache/solver_draft.cpp), [aux.hpp](https://raw.githubusercontent.com/senapk/cppaux/master/aux.hpp)
- [solver.js](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/000/.cache/solver_draft.js)

***
## Shell

```sh
#__case in
$in [1,2,3,4] 4
true
$in [1,2,3,5] 1
true
$in [1,2,5,9] 7
false
$end
```

```sh
#__case index_of
$index_of [-1,-50,-1,-99] -50
1
$index_of [-1,-50,-1,-99] -99
3
$index_of [-1,-50,-1,-99]  10
-1
$end
```

```sh
#__case find_if
$find_if [5,3,-1,-50,-1,-99]
0
$find_if [-1,-50,-1,-99,-444]
-1
$end
```

```sh
#__case min_element
$min_element [5,3,-1,-50,-1,-99]
5
$min_element [-1,-50,-1,-99,-444]
4
$min_element [-2,5,3,-1,50,-1]
0
$min_element []
-1
$end
```

```sh
#__case find_min_if
$find_min_if [5,3,-1,-50,-1,-99]
1
$find_min_if [-1,-50,-1,-99,-444]
-1
$end
```

