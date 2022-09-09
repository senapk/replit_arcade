#include <iostream>
int main() {
	int angulo { };
	std::cin >> angulo;
	angulo = angulo % 360;
	if (angulo < 0)
		angulo += 360;
	std::cout << angulo << '\n';
}