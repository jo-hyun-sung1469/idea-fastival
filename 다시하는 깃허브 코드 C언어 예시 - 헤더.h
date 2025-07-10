#ifndef RPGDLL_H
#define RPGDLL_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#define DLL_EXPORT __declspec(dllexport)
#endif
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <Windows.h>
#include <wchar.h>
#include <fcntl.h>
#include <stdint.h>

#include <locale.h> 

    // 로그 콜백
    typedef void (*LogCallback)(const char*);
    DLL_EXPORT void register_log_callback(LogCallback callback);
    DLL_EXPORT void log_message(const char* message);

    // ========== 구조체 정의 (Unity와 호환) ==========

    typedef struct {
        char name[40]; // 플레이어 이름
        int hp;
        int Max_hp;
        int attack;
        int defense;
        int level;

        // Unity 호환을 위해 함수 포인터 제거
        int skill_cooltime[5];
        int op_cooltime[6];
        uint8_t active[5];

        int critrate;
        int critdamage;
        int input;
    } Player;

    typedef struct {
        char name[40];
        int hp;
        char word_hp[40];
        int Max_hp;
        int attack;
        int defense;
        uint8_t hp_select;
    } Enemy;

    // ========== 함수 선언 (DLL 내보낼 함수들) ==========

    // 전투 관련
    DLL_EXPORT int skill_printf(Player* player, Enemy* enemy);
    DLL_EXPORT int skill_scanf(Player* player, Enemy* enemy);
    DLL_EXPORT int player_basicAttack(Player* player, Enemy* enemy);
    DLL_EXPORT void enemy_basicAttack(Player* player, Enemy* enemy);
    DLL_EXPORT void level_up(Player* player, Enemy* enemy);
    DLL_EXPORT void skill_choice(Player* player, Enemy* enemy);
    DLL_EXPORT void skill_loop(Player* player, Enemy* enemy, int i);
    DLL_EXPORT int skill_array(Player* player, Enemy* enemy);
    DLL_EXPORT void skill_pointer(Player* player, Enemy* enemy, int i);

    // 연산자 관련
    DLL_EXPORT void operator_select(Player* player, Enemy* enemy);
    DLL_EXPORT void operator_plus(Player* player, Enemy* enemy, int i);
    DLL_EXPORT void operator_multiply(Player* player, Enemy* enemy, int i);
    DLL_EXPORT void operator_divide(Player* player, Enemy* enemy, int i, int j);
    DLL_EXPORT void operator_remainder(Player* player, Enemy* enemy, int i);
    DLL_EXPORT void operator_compound_assignment(Player* player, Enemy* enemy,int i);
    DLL_EXPORT void operator_subtraction(Player* player, Enemy* enemy, int i);

    DLL_EXPORT void skill_cooltime_alarm(Player* player, Enemy* enemy, int i);
    DLL_EXPORT void init_ramdom();
    DLL_EXPORT int random(int, int);

    //player와 enemy설정
    DLL_EXPORT void playersetting(Player* player);
    DLL_EXPORT void enemysetting(Enemy*enemy,Player*player);

#ifdef __cplusplus
}
#endif

#endif