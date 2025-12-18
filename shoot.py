import pygame
import sys
import os
import random
import math

# --- 1. 定数定義 ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# 敵の種類
ENEMY_TYPE_NORMAL = 0
ENEMY_TYPE_WAVY = 1
ENEMY_TYPE_SHOOTER = 2

# ボス出現スコア間隔
BOSS_APPEAR_INTERVAL = 150

# --- 2. 必須設定 ---
# 作業ディレクトリの固定
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- クラス定義 ---

class Bullet(pygame.sprite.Sprite):
    """
    弾クラス
    自機と敵の弾を共通で管理
    """
    def __init__(self, x:float, y:float, vy:float, vx:float=0, is_player_bullet:bool=True, color:tuple=WHITE) -> None:
        """
        弾の設定
        引数 x,y: 弾の座標
        引数 vx,vy: 弾の速度
        引数 is_player_bullet: プライヤーの弾かどうか
        引数 color: 弾の色
        """
        super().__init__()
        size = 10 if is_player_bullet else 8
        self.image = pygame.Surface((size, size))
        
        if is_player_bullet:
            # プレイヤー弾は引数で色を指定可能にする
            self.image.fill(color)
        else:
            # 敵弾は赤玉
            pygame.draw.circle(self.image, RED, (size//2, size//2), size//2)
            self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vy = vy
        self.vx = vx

    def update(self) -> None:
        """
        弾の移動処理と画面外削除
        """
        self.rect.y += self.vy
        self.rect.x += self.vx
        if self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50 or self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50:
            self.kill()

class Player(pygame.sprite.Sprite):
    """
    自機の親クラス（共通機能）
    """
    def __init__(self) -> None:
        """
        自機の共通機能の設定
        """
        super().__init__()
        self.image = pygame.Surface((30, 30)) # デフォルト
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5
        self.last_shot_time = 0
        self.shoot_interval = 80
    
    def update(self) -> None:
        """
        自機の移動処理の設定
        """
        keys = pygame.key.get_pressed()
        # Shiftキーで低速移動
        current_speed = self.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            current_speed = self.speed / 2

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += current_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= current_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += current_speed

    def shoot(self) -> None:
        """
        子クラスでオーバーライド（上書き）するためのメソッド
        """
        pass

class PlayerBalance(Player):
    """
    Type A: バランス型（青）
    """
    def __init__(self) -> None:
        """
        バランス型の各種設定
        """
        super().__init__()
        self.image.fill(BLUE)
        self.speed = 5
        self.shoot_interval = 80

    def shoot(self) -> None:
        """
        バランス型の射撃機構
        """
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            # 3WAY弾 (シアン)
            bullet_centers = [0, -15, 15]
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 10
                vy = -math.cos(rad) * 10
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=CYAN)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now

class PlayerSpeed(Player):
    """
    Type B: 高速移動型（赤）
    """
    def __init__(self) -> None:
        """
        高速移動型の各種設定
        """
        super().__init__()
        self.image.fill(RED)
        self.speed = 8
        self.shoot_interval = 80 

    def shoot(self) -> None:
        """
        高速移動型の射撃機構
        """
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_interval:
            # 3WAY弾 (少し赤い白)
            bullet_centers = [0, -15, 15] 
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 10
                vy = -math.cos(rad) * 10
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=(255, 100, 100))
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now

class PlayerSwitch(Player):
    """
    Type C: 射撃モード切替型
    """
    def __init__(self) -> None:
        """
        射撃モード切替型の各種設定
        """
        super().__init__()
        self.image.fill(YELLOW)
        self.speed = 5
        self.shoot_mode = 2 # 2wayスタート
        self.last_toggle_time = 0 # 連打防止

    def shoot(self) -> None:
        """
        射撃モード切替型の射撃機構
        """
        now = pygame.time.get_ticks()
        self.shoot_interval = 80 if self.shoot_mode == 2 else 20
        if now - self.last_shot_time > self.shoot_interval:
            bullet_centers = [-10, 10] if self.shoot_mode == 2 else [0]
            for angle in bullet_centers:
                rad = math.radians(angle)
                vx = math.sin(rad) * 10
                vy = -math.cos(rad) * 10
                bullet = Bullet(self.rect.centerx, self.rect.top, vy, vx, is_player_bullet=True, color=YELLOW)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
            self.last_shot_time = now
        
    def toggle_mode(self) -> None:
        """
        射撃モード切替型専用
        Xキーで射撃モード切替
        """
        now = pygame.time.get_ticks()
        if now -self.last_toggle_time > 300: # 0.3秒クールタイム
            self.shoot_mode = 1 if self.shoot_mode == 2 else 2
            self.last_toggle_time = now

class Enemy(pygame.sprite.Sprite):
    """
    ザコ敵クラス
    タイプに応じて動作を変更
    """
    def __init__(self, enemy_type:int) -> None:
        """
        敵の設定
        引数 enemy_type: 敵のタイプの種類
        """
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((30, 30))
        
        if self.enemy_type == ENEMY_TYPE_NORMAL:
            self.image.fill(RED)
            self.speed_y = 3
        elif self.enemy_type == ENEMY_TYPE_WAVY:
            self.image.fill(GREEN)
            self.speed_y = 2
            self.t = 0
        elif self.enemy_type == ENEMY_TYPE_SHOOTER:
            self.image.fill(YELLOW)
            self.speed_y = 1
            self.shoot_timer = 0

        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -50

    def update(self) -> None:
        """
        敵の挙動処理
        """
        self.rect.y += self.speed_y

        if self.enemy_type == ENEMY_TYPE_WAVY:
            self.t += 0.1
            self.rect.x += math.sin(self.t) * 5
        elif self.enemy_type == ENEMY_TYPE_SHOOTER:
            self.shoot_timer += 1
            if self.shoot_timer > 120:
                self.shoot_at_player()
                self.shoot_timer = 0

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def shoot_at_player(self) -> None:
        """
        プレイヤーに狙い撃ちする弾を発射
        """
        if player: # プレイヤーが存在する場合のみ
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            speed = 5
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullet = Bullet(self.rect.centerx, self.rect.centery, vy, vx, is_player_bullet=False)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

class Boss(pygame.sprite.Sprite):
    """
    ボスクラス
    """
    def __init__(self, level:int=1) -> None:
        """
        ボスの設定
        引数 level: ボスのレベル(HPや弾幕の強度に影響)
        """
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, -100)
        
        self.max_hp = 100 * level
        self.hp = self.max_hp
        self.state = "entry"
        self.angle = 0
        self.timer = 0

    def update(self) -> None:
        """
        ボスの行動更新
        """
        if self.state == "entry":
            self.rect.y += 2
            if self.rect.y >= 100:
                self.state = "battle"
        
        elif self.state == "battle":
            self.timer += 1
            self.rect.x = (SCREEN_WIDTH // 2) + math.sin(self.timer * 0.05) * 150
            
            if self.timer % 5 == 0:
                self.shoot_danmaku()

    def shoot_danmaku(self) -> None:
        """
        回転弾幕を発射
        """
        self.angle += 12
        bullet_speed = 4
        for i in range(0, 360, 90):
            theta = math.radians(self.angle + i)
            vx = math.cos(theta) * bullet_speed
            vy = math.sin(theta) * bullet_speed
            bullet = Bullet(self.rect.centerx, self.rect.centery, vy, vx, is_player_bullet=False)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

# --- 3. ゲーム初期化 ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("東方風シューティング")
clock = pygame.time.Clock()

# フォント設定
try:
    font = pygame.font.SysFont("meiryo", 40)
    small_font = pygame.font.SysFont("meiryo", 24)
except:
    font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 24)

# グループ作成
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

player = None # プレイヤーインスタンス用

# ゲーム変数
score = 0
next_boss_score = BOSS_APPEAR_INTERVAL
boss_level = 1
is_boss_active = False
selected_char_idx = 0 # 0:TypeA, 1:TypeB 2:TypeC

# ゲーム状態定義
GAME_STATE_TITLE = 0
GAME_STATE_SELECT = 1
GAME_STATE_PLAYING = 2
GAME_STATE_GAMEOVER = 3
current_state = GAME_STATE_TITLE

# --- 4. ゲームループ ---
running = True
while running:
    # --- イベント処理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # ■ タイトル画面
        if current_state == GAME_STATE_TITLE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_state = GAME_STATE_SELECT # 選択画面へ
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # ■ キャラ選択画面
        elif current_state == GAME_STATE_SELECT:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_char_idx = (selected_char_idx - 1) % 3
                if event.key == pygame.K_RIGHT:
                    selected_char_idx = (selected_char_idx + 1) % 3
                if event.key == pygame.K_SPACE or event.key == pygame.K_z:
                    # ゲーム開始初期化処理
                    all_sprites.empty()
                    enemies.empty()
                    boss_group.empty()
                    player_bullets.empty()
                    enemy_bullets.empty()
                    
                    # ★ここでクラスを使い分ける
                    if selected_char_idx == 0:
                        player = PlayerBalance()
                    elif selected_char_idx == 1:
                        player = PlayerSpeed()
                    else:
                        player = PlayerSwitch()
                        
                    all_sprites.add(player)
                    
                    score = 0
                    next_boss_score = BOSS_APPEAR_INTERVAL
                    boss_level = 1
                    is_boss_active = False
                    current_state = GAME_STATE_PLAYING
                if event.key == pygame.K_ESCAPE:
                    current_state = GAME_STATE_TITLE # 戻る

        # ■ ゲームオーバー画面
        elif current_state == GAME_STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                current_state = GAME_STATE_TITLE

    # --- 更新処理 ---
    if current_state == GAME_STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            player.shoot()
        if isinstance(player, PlayerSwitch) and keys[pygame.K_x]:
            player.toggle_mode()

        if not is_boss_active and score >= next_boss_score:
            is_boss_active = True
            boss = Boss(boss_level)
            all_sprites.add(boss)
            boss_group.add(boss)
            for e in enemies:
                score += 10
                e.kill()

        if not is_boss_active:
            if random.random() < 0.03: 
                t_type = random.choice([ENEMY_TYPE_NORMAL, ENEMY_TYPE_WAVY, ENEMY_TYPE_SHOOTER])
                enemy = Enemy(t_type)
                all_sprites.add(enemy)
                enemies.add(enemy)
        
        all_sprites.update()

        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            score += 10

        if is_boss_active:
            boss_hits = pygame.sprite.groupcollide(boss_group, player_bullets, False, True)
            for boss_sprite, bullets in boss_hits.items():
                for b in bullets:
                    boss_sprite.hp -= 1
                    score += 1
                if boss_sprite.hp <= 0:
                    score += 1000
                    boss_sprite.kill()
                    is_boss_active = False
                    boss_level += 1
                    next_boss_score = score + BOSS_APPEAR_INTERVAL

        if pygame.sprite.spritecollide(player, enemies, False) or \
           pygame.sprite.spritecollide(player, enemy_bullets, False) or \
           pygame.sprite.spritecollide(player, boss_group, False):
            current_state = GAME_STATE_GAMEOVER

    # --- 描画処理 ---
    screen.fill(BLACK)

    if current_state == GAME_STATE_TITLE:
        title_text = font.render("東方風シューティング", True, WHITE)
        start_text = font.render("スペースキーで次へ", True, YELLOW)
        quit_text = small_font.render("ESCキーで終了", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

    elif current_state == GAME_STATE_SELECT:
        sel_title = font.render("キャラクター選択", True, WHITE)
        screen.blit(sel_title, (SCREEN_WIDTH//2 - sel_title.get_width()//2, 100))
        
        # キャラクターのプレビュー描画（四角形を表示）
        box_width = 100
        box_height = 100
        spacing = 180
        center_y = SCREEN_HEIGHT // 2 - 50
        center_x = SCREEN_WIDTH // 2

        rect_positions = [
            center_x - spacing - box_width//2,
            center_x - box_width//2,
            center_x + spacing - box_width//2
        ]

        # Type A
        color_a = BLUE if selected_char_idx == 0 else (50, 50, 100)
        rect_a = pygame.Rect(rect_positions[0], center_y, 100, 100)
        pygame.draw.rect(screen, color_a, rect_a)
        name_a = small_font.render("TypeA:バランス", True, WHITE)
        screen.blit(name_a, (rect_a.centerx - name_a.get_width()//2, rect_a.bottom + 10))

        # Type B
        color_b = RED if selected_char_idx == 1 else (100, 50, 50)
        rect_b = pygame.Rect(rect_positions[1], center_y, 100, 100)
        pygame.draw.rect(screen, color_b, rect_b)
        name_b = small_font.render("TypeB:高速移動", True, WHITE)
        screen.blit(name_b, (rect_b.centerx - name_b.get_width()//2, rect_b.bottom + 10))
        
        # Type C
        color_c = YELLOW if selected_char_idx == 2 else (100, 100, 50)
        rect_c = pygame.Rect(rect_positions[2], center_y, 100, 100)
        pygame.draw.rect(screen, color_c, rect_c)
        name_c = small_font.render("TypeC:射撃切替", True, WHITE)
        screen.blit(name_c, (rect_c.centerx - name_c.get_width()//2, rect_c.bottom + 10))

        # 選択枠の強調
        if selected_char_idx == 0:
            pygame.draw.rect(screen, YELLOW, rect_a, 5)
        elif selected_char_idx == 1:
            pygame.draw.rect(screen, YELLOW, rect_b, 5)
        else:
            pygame.draw.rect(screen, YELLOW, rect_c, 5)

        guide_text = small_font.render("← → で選択 / Z or SPACE で決定", True, YELLOW)
        screen.blit(guide_text, (SCREEN_WIDTH//2 - guide_text.get_width()//2, SCREEN_HEIGHT - 100))

    elif current_state == GAME_STATE_PLAYING:
        all_sprites.draw(screen)
        score_text = small_font.render(f"スコア: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        if not is_boss_active:
            next_text = small_font.render(f"ボスまで: {next_boss_score - score}", True, YELLOW)
            screen.blit(next_text, (10, 40))
        if is_boss_active:
            for b in boss_group:
                pygame.draw.rect(screen, RED, (100, 20, 400, 20))
                hp_ratio = b.hp / b.max_hp
                pygame.draw.rect(screen, GREEN, (100, 20, 400 * hp_ratio, 20))
                pygame.draw.rect(screen, WHITE, (100, 20, 400, 20), 2)
                hp_text = small_font.render(f"Boss HP: {b.hp}", True, WHITE)
                screen.blit(hp_text, (100, 45))

    elif current_state == GAME_STATE_GAMEOVER:
        over_text = font.render("ゲームオーバー", True, RED)
        score_res_text = font.render(f"最終スコア: {score}", True, WHITE)
        retry_text = small_font.render("Rキーでタイトルへ", True, WHITE)
        screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(score_res_text, (SCREEN_WIDTH//2 - score_res_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(retry_text, (SCREEN_WIDTH//2 - retry_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()