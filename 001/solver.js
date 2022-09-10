class Calculator {
    batteryMax;
    battery;
    display;

    //Inicia os atributos, battery e display começam com o zero.
    constructor(batteryMax) { // todo 
    }

    //Aumenta a bateria, porém não além do máximo.
    chargeBattery(value) { // todo  
    }

    //Tenta gastar uma unidade da bateria e emite um erro se não conseguir.
    useBattery() { // todo  
    }

    //Se conseguir gastar bateria, armazene a soma no atributo display.
    sum(a, b) { // todo  
    }

    //Se conseguir gastar bateria e não for divisão por 0.
    division(num, den) { // todo 
    }

    //Retorna o conteúdo do display com duas casas decimais.
    toString() { 
        return "display = " + this.display.toFixed(2) + ", battery = " + this.battery;
    }
}

function main() {
    let chain = new Map();
    let ui = [];
    let calc = new Calculator(0);

    chain.set("show",   () => print("" + calc));
    chain.set("init",   () => calc = new Calculator(+ui[1]));
    chain.set("charge", () =>    calc.chargeBattery(+ui[1]));
    chain.set("sum",    () =>              calc.sum(+ui[1], +ui[2]));
    chain.set("div",    () =>         calc.division(+ui[1], +ui[2]));

    execute(chain, ui);
}

// ------------ Funções de Leitura --------------------

// Caso não interativo via moodle
let __lines = require("fs").readFileSync(0).toString().split("\n");
let input = () => __lines.shift();

// Caso interativo via readline
// let readline = require("readline-sync")
// let input = () => readline.question();

// ------------ Funções de Escrita --------------------

let write = text => process.stdout.write("" + text);
let print = text => console.log(text);

// ------------ Funções de Formatação --------------------

// Função auxiliar para converter de string para vetor
// "[1,2,3,4]" para [1, 2, 3, 4]
function to_vet(token) {
    let size = token.length;
    let inside = token.substring(1, size - 1);
    return inside === "" ? [] : inside.split(",").map(x => +x)
}

//Converte de vetor para string sem inserir os espaços
//[1, 2, 3, 4] => "[1,2,3,4]"
function fmt(vet) {
    return "[" + vet.join(", ") + "]";
}

// ------------ Funções do Shell --------------------


let execute = (chain, ui) => __shell(chain, ui, true);
let shell   = (chain, ui) => __shell(chain, ui, false);

function __shell(chain, ui, on_moodle) {
    while (true) {
        if (!on_moodle)
            write("$")
        let line = input();
        if (on_moodle)
            print("$" + line);
        ui.splice(0); //apagar tudo
        line.split(" ").forEach(x => ui.push(x));
        
        let cmd = ui[0];
        if (cmd == "end") {
            return;
        } else if (chain.has(cmd)) {
            chain.get(cmd)();
        } else {
            print("fail: command not found");
        }
    }
}

main()


