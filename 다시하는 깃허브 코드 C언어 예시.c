#pragma execution_character_set("utf-8")
#include "다시하는 깃허브 코드 C언어 예시 - 헤더.h"// 여긴 헤더파일 이름에 따라 바뀜

__declspec(dllexport) void skill_pointer(Player* player, Enemy* enemy, int i)
{
	if (player->level < 40)
	{
		log_message("현재 사용할 수 없는 레벨 입니다\n");
		return;
	}
	else
	{
		if (enemy->hp_select == 1)
		{
			enemy->hp_select = 0;

			if (player->level < 43)
				player->skill_cooltime[5] = 11;
			else if (player->level < 46 && player->level >= 43)
				player->skill_cooltime[5] = 10;
			else if (player->level < 48 && player->level >= 46)
				player->skill_cooltime[5] = 9;
			else if (player->level < 50 && player->level >= 48)
				player->skill_cooltime[5] = 8;

			return;
		}
		else
		{
			int choice10 = 0,memory = 0, damage = 0, damage1 = 0, a = 0, b = 100, critrate_count = 0;
			char logbuf[1000];


			if (i == 1)
			{
				damage = player->attack;
				critrate_count = random(a, b);
				if (player->critrate >= critrate_count)
				{
					damage *= player->critdamage;
					log_message("크리티컬 발생!\n");
				}
				enemy->hp -= damage;

				if (enemy->hp < 0 || enemy->hp > enemy->Max_hp)
				{
					enemy->hp = 0;
				}

				snprintf(logbuf, sizeof(logbuf), "player가 포인터 스킬을 사용하고 공격해서 %d만큼의 데미지를 입혔습니다(%s의 체력 : %d)\n", damage, enemy->name, enemy->hp);
				log_message(logbuf);
			}
			else if (i == 2)
			{
				damage = player->attack * 2;
				critrate_count = random(a, b);
				if (player->critrate >= critrate_count)
				{
					damage *= player->critdamage;
					log_message("크리티컬 발생!\n");
				}
				enemy->hp -= damage;
		
				if (enemy->hp < 0 || enemy->hp > enemy->Max_hp)
				{
					enemy->hp = 0;
				}

				player->skill_cooltime[0] = memory;
				snprintf(logbuf, sizeof(logbuf), "player가 포인터 스킬을 사용하고 printf스킬을 사용해서 %d만큼의 데미지를 입혔습니다(%s의 체력 : %d)\n", damage, enemy->name, enemy->hp);
				log_message(logbuf);
			}
			else if (i == 3)
			{
				memory = player->skill_cooltime[1];
				player->skill_cooltime[1] = 0;

				enemy->hp -= (int)(skill_scanf(player, enemy) * 2);
				if (enemy->hp < 0 || enemy->hp > enemy->Max_hp)
				{
					enemy->hp = 0;
				}
					player->skill_cooltime[1] = memory;
				snprintf(logbuf, sizeof(logbuf), "player가 포인터 스킬을 사용하고 scanf스킬을 사용해서 %d만큼의 데미지를 입혔습니다(%s의 체력 : %d)\n", damage, enemy->name, enemy->hp);
				log_message(logbuf);
			}
			else if (i == 4)
			{

				for (int i = 0; i < 5; i++)
				{
					damage1 += player->attack;
					
					critrate_count = random(a, b);

					if (player->critrate >= critrate_count)
					{
						damage1 *= player->critdamage;
						log_message("크리티컬 발생!\n");
					}
					damage += damage1;
				}


				enemy->hp -= damage;
				if (enemy->hp < 0 || enemy->hp > enemy->Max_hp)
				{
					enemy->hp = 0;
				}
				
				snprintf(logbuf, sizeof(logbuf), "player가 포인터 스킬을 사용하고 array스킬을 사용해서 %d만큼의 데미지를 입혔습니다(%s의 체력 : %d)\n", damage, enemy->name, enemy->hp);
				log_message(logbuf);

			}

			if (player->level < 43)
				player->skill_cooltime[5] = 11;
			else if (player->level < 46 && player->level >= 43)
				player->skill_cooltime[5] = 10;
			else if (player->level < 48 && player->level >= 48)
				player->skill_cooltime[5] = 9;
			else if (player->level < 50 && player->level >= 48)
				player->skill_cooltime[5] = 8;
		}
	}
}