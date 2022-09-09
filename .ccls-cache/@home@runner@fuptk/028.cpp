#include <cstdio>
#include <iostream>
int main(){
    int n, x, y, s;
    char c;
		std::cin >> n >> x >> y >> c >> s;

    if(c == 'R') {
		x += s;
		x = (((x % n) + n) % n);
	}
        
    else if(c == 'R') {
		x -= s;
		x = (((x % n) + n) % n);
	}
        
    else if(c == 'U') {
		y -= s;
		y = (((y % n) + n) % n);
	}
        
    else if(c == 'D') {
		y += s;
		y = (((y % n) + n) % n);
	}
            
    printf("%d %d\n", x, y);
    return 0;
}
