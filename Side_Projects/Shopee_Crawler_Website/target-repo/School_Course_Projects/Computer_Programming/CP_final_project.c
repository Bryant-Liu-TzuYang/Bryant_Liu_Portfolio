#include <stdio.h>

typedef struct{
    int info[16][16];
}Flag;

int dx[16] = {0, 1, 0, -1, 1, 1, -1, -1, -2, -2, -1, 1, 2, 2, 1, -1};
int dy[16] = {1, 0, -1, 0, -1, 1, 1, -1, 1, -1, -2, -2, 1, -1, 2, 2};
int ez[8][2] = {{}, {}, {}, {4, 8}, {0, 4}, {0, 8}, {0, 8}};

int N, min = 35;

int in(int x, int y){
    return x >= 0 && y >= 0 && x < N && y < N;
}

void init(Flag *flag){
    for(int i = 0; i < N; i++){
        for(int j = 0; j < N; j++){
            flag->info[i][j] = 0;
        }
    }
}

void dfs(int board[][16], int x, int y, int rem, int steps, Flag flag){
    if(rem + steps - 1 >= min) return;
    if(rem == 1){
        min = steps;
        return;
    }

    int nx, ny, toc = 0, wall, race = board[x][y];
    Flag new;
    switch(race){
        case 1:
            if(in(x - 1, y) && board[x - 1][y] == 0){
                board[x][y] = 0;
                board[x - 1][y] = 1;
                dfs(board, x - 1, y, rem, steps + 1, flag);
                board[x][y] = 1;
                board[x - 1][y] = 0;
            }
            if(in(x - 1, y + 1) && board[x - 1][y + 1] > 0 && board[x - 1][y + 1] < 7){
                board[x][y] = 0;
                dfs(board, x - 1, y + 1, rem - 1, steps + 1, flag);
                board[x][y] = 1;
            }
            if(in(x - 1, y - 1) && board[x - 1][y - 1] > 0 && board[x - 1][y - 1] < 7){
                board[x][y] = 0;
                dfs(board, x - 1, y - 1, rem - 1, steps + 1, flag);
                board[x][y] = 1;
            }
            return;

        case 2:
            for(int i = 8; i < 16; i++){
                nx = x + dx[i];
                ny = y + dy[i];
                if(in(nx, ny) && board[nx][ny] < 7 && !flag.info[nx][ny]){
                    if(board[nx][ny] > 0) init(&new);
                    else board[nx][ny] = 2, toc = flag.info[x][y] = 1;

                    board[x][y] = 0;
                    dfs(board, nx, ny, (toc)? rem:rem - 1, steps + 1, (toc)? flag:new);
                    board[x][y] = 2;

                    if(toc) toc = board[nx][ny] = flag.info[x][y] = 0;
                }
            }
            return;

        default:
            for(int i = ez[race][0]; i < ez[race][1]; i++){
                wall = 0;
                for(int j = 1; j <= (race < 6)? N:1; j++){
                    nx = x + dx[i]*j;
                    ny = y + dy[i]*j;
                    if(in(nx, ny) && board[nx][ny] < 7 && !flag.info[nx][ny]){
                        if(board[nx][ny] > 0){
                            init(&new);
                            wall = 1;
                        }
                        else board[nx][ny] = race, toc = flag.info[x][y] = 1;

                        board[x][y] = 0;
                        dfs(board, nx, ny, (toc)? rem:rem - 1, steps + ((race == 6)? j:1), (toc)? flag:new);
                        board[x][y] = race;

                        if(toc) toc = board[nx][ny] = flag.info[x][y] = 0;

                        if(!wall) continue;
                    }
                    break;
                }
            }
            return;
    }
}

int count(int board[][16], int *rem){
    for(int i = 0; i < N; i++){
        for(int j = 0; j < N; j++){
            if(board[i][j] > 0 && board[i][j] < 7){
                (*rem)++;
            }
        }
    }
}

int main(){
    int x, y, rem = 0;
    int board[16][16] = {{0}};
    Flag flag;

    scanf("%d", &N);
    for(int i = 0; i < N; i++){
        for(int j = 0; j < N; j++){
            scanf("%d", &board[i][j]);
        }
    }
    scanf("%d%d", &x, &y);
    
    init(&flag);
    count(board, &rem);
    dfs(board, x, y, rem, 0, flag);

    printf("%d\n", min);
}
