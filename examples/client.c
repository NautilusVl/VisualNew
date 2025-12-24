#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

int main() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(65432);
    inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);
    connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
    char* message = "Hello from C!";
    send(sock, message, strlen(message), 0);
    char buffer[1024] = {0};
    recv(sock, buffer, sizeof(buffer), 0);
    printf("Received: %s\n", buffer);
    close(sock);
    return 0;
}