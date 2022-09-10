class Car{
    pass; // Passageiros
    passMax; // limite de Passageiros
    gas; // tanque
    gasMax; // limite do tanque
    km; // quantidade de quilometragem

    constructor() {
      this.pass = 0;
      this.passMax = 2;
      this.gas = 0;
      this.gasMax = 100;
      this.km = 0;
    }
    toString() { // todo 
      return "pass: " + this.pass + ", gas: " + this.gas + ", km: " + this.km;
    }

    enter() { // todo 
      if (this.pass == this.passMax)
        console.log("fail: limite de pessoas atingido");
      else
        this.pass += 1;
    }

    leave() { // todo 
      if (this.pass == 0)
        console.log("fail: nao ha ninguem no carro");
      else
        this.pass -= 1;
    }
    
    fuel(gas) { // todo 
    }

    drive (km) { // todo 
    }    
};

let car = new Car();
console.log(car);
car.pass += 1;
console.log(car);

