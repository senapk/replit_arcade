#include <iostream>
#include <sstream>
#include <iomanip>
#include <aux.hpp>

struct Calculator {
    int batteryMax;
    int battery;
    float display;

    //Inicia os atributos, battery e display começam com o zero.
    Calculator(int batteryMax) { // todo
    }

    //Aumenta a bateria, porém não além do máximo.
    void chargeBattery(int value) { // todo 
    }

    //Tenta gastar uma unidade da bateria e emite um erro se não conseguir.
    bool useBattery() {
        return {}; // todo 
    }

    //Se conseguir gastar bateria, armazene a soma no atributo display.
    void sum(int a, int b) { // todo 
    }

    //Se conseguir gastar bateria e não for divisão por 0.
    void division(int num, int den) { // todo
    }

    //Retorna o conteúdo do display com duas casas decimais.
    std::string str() { 
        std::stringstream ss;
        ss << "display = " << std::fixed << std::setprecision(2) << this->display;
        ss << ", battery = " << this->battery;
        return ss.str();
    }
};

std::ostream& operator<<(std::ostream& os, Calculator c) {
    return (os << c.str());
}

int main() {
    Calculator c(0);
    aux::Chain chain;
    aux::Param ui;

    auto to_int = aux::to<int>;

    chain["show"]   = [&]() { std::cout << c << std::endl;                   };
    chain["init"]   = [&]() {  c = Calculator(to_int(ui[1]));                };
    chain["charge"] = [&]() { c.chargeBattery(to_int(ui[1]));                };
    chain["sum"]    = [&]() {           c.sum(to_int(ui[1]), to_int(ui[2])); };
    chain["div"]    = [&]() {      c.division(to_int(ui[1]), to_int(ui[2])); };

    aux::execute(chain, ui);
}

