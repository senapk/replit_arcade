## @003 Motoca & Motoca de parquinho com uma criança

![](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/003/cover.jpg)

[](toc)

- [Intro](#intro)
- [Guide](#guide)
    - [Ajuda](#ajuda)
    - [Adaptações para C++](#adaptações-para-c)
- [Draft](#draft)
- [Shell](#shell)
[](toc)

Você já deve ter ido em algum parque e viu crianças de 4 a 10 anos andando naquelas motocas motorizadas. Pois é, nós vamos modelar e implementar uma delas.

## Intro

- Você deverá implementar a classe `Pessoa` e a class `Moto`.
- Iniciar
    - A moto inicia com 1 de potência, sem minutos e sem ninguém.
- Subir
    - Só pode estar uma pessoa na moto por vez. Para subir, informe nome e idade de quem está subindo.
- Descer
    - Só pode descer se tiver alguém na moto.
- Comprar tempo
    - O tempo em minutos é comprado e enquanto houver tempo, qualquer pessoa pode dirigir.
- Dirigir tempo
    - Se houver uma pessoa com 10 anos ou menos e houver minutos, então ela pode passear de moto.
    - Se o tempo acabar no meio do passeio, informe o quanto a pessoa andou.
- Buzinar
    - Qualquer pessoa pode buzinar(honk)
    - O barulho da buzina é "Pem", porém o número de `e` é igual ao valor da potência.
    - Ex: se a potência for 5, buzinar deve gerar: Peeeeem


***
## Guide
![](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/003/diagrama.png)


### Ajuda
    - Lembre de inicializar o objeto `Pessoa` antes de chamar o método embarcar.
    - Para buzinar, utilize o `for` gerando várias vezes o `e`. 


### Adaptações para C++
A Pessoa é representado por uma instância de um shared_ptr<Person>.

```cpp
class Motorcycle {
- person : shared_ptr<Person>
__
+ enter(person : shared_ptr<Person>) : boolean
+ leave() : shared_ptr<Person>
}
```

***
## Draft
- [Solver.java](https://raw.githubusercontent.com/qxcodepoo/arcade/master/base/003/.cache/solver_draft.java)


***
## Shell

```bash

#__case subindo e buzinando
$show
potencia: 1, minutos: 0, pessoa: null
$honk
fail: moto vazia
$enter marcos 4
$show
potencia: 1, minutos: 0, pessoa: [marcos:4]
$honk
Pem
$enter marisa 2
fail: moto ocupada
$show
potencia: 1, minutos: 0, pessoa: [marcos:4]
$end
```

```bash
#__case subindo e buzinando
$init 5
$show
potencia: 5, minutos: 0, pessoa: null
$enter marcos 4
$show
potencia: 5, minutos: 0, pessoa: [marcos:4]
$honk
Peeeeem
$end
```

```bash
#__case subindo e trocando
$init 7
$enter heitor 6
$show
potencia: 7, minutos: 0, pessoa: [heitor:6]
$leave
$leave
fail: moto vazia
$enter suzana 8
$show
potencia: 7, minutos: 0, pessoa: [suzana:8]
$end
```

```bash
#__case passeando
$init 7
$enter suzana 8
$drive 10
fail: tempo zerado
$buy 40
$show
potencia: 7, minutos: 40, pessoa: [suzana:8]
$drive 20
$show
potencia: 7, minutos: 20, pessoa: [suzana:8]
$end
```

```bash
#__case nem grande nem pequeno
$init 7
$buy 20
$enter andreina 23
$drive 15
fail: muito grande para andar de moto
$show
potencia: 7, minutos: 20, pessoa: [andreina:23]
$end
```

```bash
#__case acabou o tempo
$init 7
$buy 20
$enter andreina 6
$drive 15
$show
potencia: 7, minutos: 5, pessoa: [andreina:6]
$drive 10
fail: andou 5 min e acabou o tempo
$end
```





