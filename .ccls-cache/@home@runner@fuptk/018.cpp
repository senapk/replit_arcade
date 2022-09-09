#include <iostream>
#include <cmath>
int main() {
	char opcao { };
	double number { };
	std::cin >> opcao >> number;

	if (opcao == 'c') {
		std::cout << ceil(number) << '\n';
	} else if (opcao == 'R') {
		std::cout << round(number) << '\n';
	} else {
		std::cout << floor(number) << '\n';
	}
}