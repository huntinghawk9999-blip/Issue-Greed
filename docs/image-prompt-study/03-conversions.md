# 03. 변환 예시: 테스트용 GPT 프롬프트 → 각 모델

## 0. 두 버전의 차이

- **A. 원본 의도판:** GPT 프롬프트의 지시를 그대로 옮기고, 형식과 길이만 각 모델에 맞췄어요.
- **B. 보정판:** 원본에서 모델이 임의로 처리하거나 부딪칠 수 있는 지점을 고쳤어요. 고친 내용은 아래 표에 있어요.

### 보정판에서 바꾼 것

| # | 원본 | 문제 | 보정 | 근거 |
|---|---|---|---|---|
| 1 | "One knee is raised" | 어느 무릎인지 없음. 좌우 규칙이 이 부분에만 빠져 있음 | 오른쪽 무릎을 올리고 오른발은 책상 위에 평평하게(**보는 사람 기준 왼쪽**). 왼다리는 책상 앞 모서리로 내리고 발은 공중에 편하게(보는 사람 기준 오른쪽) | GPT 교훈: 지시 없는 부위는 임의 처리. 양발에 다른 지시 |
| 2 | 손 지시 없음 | 손이 임의로 처리됨 | 오른손은 올린 무릎 위, 왼손은 엉덩이 옆 책상 위에 짚기 | 같음 |
| 3 | "front edge" + "laptop in the foreground between the camera and her lower torso" | **물리적 충돌.** 책상 앞 모서리에 앉아 카메라를 보고 있으면 책상 윗면은 인물 뒤나 옆에 있어요. 노트북이 카메라와 인물 사이에 오려면 책상의 다른 부분이 카메라 쪽으로 뻗어 있어야 해요 | 책상 **모서리**에 앉고, 책상 앞 모서리가 보는 사람 기준 오른쪽에서 카메라 쪽으로 비스듬히 뻗어 있으며, 노트북은 카메라에 더 가까운 그 부분에 놓임 | GPT 교훈: 물리적 충돌 |
| 4 | 85mm + "several meters" + "broadly enough to show... library" | 85mm는 화각이 좁아요. 풀프레임 세로 기준 세로 화각은 약 24°라서, 4m 거리면 높이 약 1.7m만 담겨요. 앉은 인물 + 책상 + 책장까지 담으려면 5m 이상 떨어져야 해요 | "about five meters away", "full body" 명시. mm 숫자보다 거리와 전신 지시를 우선 | 화각 계산 [판단] |
| 5 | "eye-level-to-desk-level" | 높이가 범위로 주어져 정해지지 않음 | "camera at her chest height" | GPT 규칙: 한 줄에 한 지시 |
| 6 | 역광 + 얼굴에 따뜻한 하이라이트 | 근거 없이 둘 다 원하면 모델이 한쪽을 버리기 쉬움 | 창을 보는 사람 기준 왼쪽 뒤에 두고 → 머리·어깨 림 라이트 + 얼굴 한쪽 측면광. 반대쪽은 그늘이고 **원본에 있던** 램프 빛으로 살짝 밝힘. 반사판 같은 새 소품은 넣지 않았어요 | 물리적 근거 부여 |
| 7 | "35mm Kodak Portra 400" | 렌즈 초점거리 85mm와 숫자가 겹침 | 태그형에서는 `kodak portra 400`만 쓰고, 문장형에서는 "shot on Kodak Portra 400 film" | 01-models.md §4 |
| 8 | "FRONT EDGE" 같은 대문자 강조 | CLIP은 소문자와 똑같이 처리하고, T5는 대문자 단어를 잘게 쪼갬 | 소문자 + 앞쪽 배치 | 토크나이저 직접 확인 |
| 9 | 얼굴·몸 질감 통일 | GPT에서 효과 확인 | 유지하되 "face, neck and hands"처럼 화면에 보이는 부위로 | GPT 교훈 |

참고로 1번(어느 무릎)과 6번(창 위치)은 제가 고른 값이에요. 반대쪽이 좋으시면 좌우만 바꾸면 돼요. 이때 손, 발, 빛의 좌우도 같이 바꿔야 서로 맞아요.

### 길이 확인 (실제 토크나이저로 계산)

| 프롬프트 | 글자 수 | CLIP 토큰 | T5 토큰 | 제한 |
|---|---|---|---|---|
| 원본 GPT | 3,563 | 688 | 815 | — |
| Lustify A | 949 | 203 | — | 1,500자 |
| Lustify B | 1,127 | 245 | — | 1,500자 |
| Lustify 네거티브 | 331 | 81 | — | 1,500자 |
| Chroma A | 1,456 | — | 354 | 7,500자 / T5 512 |
| Chroma B | 1,977 | — | 484 | 7,500자 / T5 512 |
| Chroma Flash B | 1,905 | — | 476 | T5 512 |
| WAI | 384 | 91 | — | 1,500자 |

---

## 1. Lustify v8 (Venice)

### A. 원본 의도판

**포지티브**
```
photograph of a 28 year old adult East Asian woman sitting casually on the front corner of a dark mahogany desk in an old private library, one knee raised onto the desk, other leg hanging down over the desk edge, torso leaning slightly toward the camera, bright natural smile, looking at viewer, long straight black hair, curvy healthy figure, fitted white button-down shirt with unbuttoned collar, open silver laptop on the desk in the foreground partially covering her lap, brass desk lamp, floor-to-ceiling bookshelves with antique books, burgundy velvet curtains, tall window behind her, brown leather armchair, warm late afternoon sunlight through the window, chiaroscuro, rim light on hair, dark moody interior, shallow depth of field, bokeh, eye-level shot, full body, 85mm lens, kodak portra 400, film grain, halation, natural skin texture, visible pores, subtle facial asymmetry, individual hair strands, cotton fabric folds, high aesthetic
```

### B. 보정판

**포지티브**
```
photograph of a 28 year old adult East Asian woman sitting on the front corner of a dark mahogany desk in an old private library, seen from a front three-quarter angle, camera at her chest height, full body, her right knee raised with her right foot flat on the desk top on the viewer's left, her left leg hanging down over the desk edge on the viewer's right with the foot relaxed in the air, her right hand resting on her raised knee, her left hand flat on the desk beside her hip, torso leaning slightly forward, bright natural smile, looking at viewer, long straight black hair, curvy healthy figure, fitted white button-down shirt with unbuttoned collar, open silver laptop on the near part of the desk closer to the camera, partially covering her hips, brass desk lamp, floor-to-ceiling bookshelves, burgundy velvet curtains, tall window behind her on the viewer's left, warm sunlight from behind left, rim light on hair and shoulders, soft shadow on the side of her face away from the window, warm lamp glow, kodak portra 400, film grain, halation, natural skin texture, visible pores, same skin texture on face and body
```

**네거티브 (A·B 공통)**
```
cgi, 3d render, illustration, anime, painting, airbrushed skin, plastic skin, waxy skin, oversharpened, oversaturated, hdr, glossy, beauty filter, collage, split screen, multiple views, border, text, watermark, extra fingers, extra limbs, deformed feet, twisted ankle, wide-angle distortion, fisheye, teenager, childlike, aged down
```

**권장 설정**

| 항목 | 값 | 비고 |
|---|---|---|
| 비율 / 해상도 | 9:16, API 기준 720×1280 | Venice 웹 비율 선택 시 실제 픽셀은 확인 안 됨 |
| 스텝 | 30 (Venice 기본값) | [제작자 샘플] 30 |
| CFG | 3.5~4 | [제작자 샘플]. Venice 웹 기본 CFG는 확인 안 됨 |
| 스타일 프리셋 | 없음 | 프리셋이 글자 수를 같이 씀 |
| 프롬프트 향상 | 끔 | 의도 변경 방지 |
| 시드 | 고정해서 지시 하나씩 바꿔 가며 비교 | |

**참고**

- B의 좌우·손 지시는 SDXL에서 **지켜지지 않을 수 있어요.** 그래도 앞쪽 청크에 두면 같은 시드에서 따를 확률은 올라가요 [판단]. 확실하게 하려면 로컬 포즈 ControlNet이나 Venice 인페인팅으로 보정해요.
- `high aesthetic`은 제작자 샘플에 반복해서 나오는 태그예요. 효과가 공식적으로 설명된 건 아니에요.
- 네거티브의 `teenager, childlike, aged down`은 성인 외모를 유지하기 위한 안전장치예요. 포지티브의 `28 year old adult`와 같이 써요.

## 2. Lustify SDXL (Venice)

Venice에 등록된 버전을 확인하지 못해서, 프롬프트는 **Lustify v8과 같은 걸** 쓰고 설정만 이렇게 바꾸는 걸 권해요.

| 항목 | 값 |
|---|---|
| 스텝 | 25~30 (Venice 기본 20) |
| CFG | 4~5에서 시작. 근거가 없는 값이라 시드를 고정하고 3.5 / 5 / 6.5로 비교해 보세요 [판단] |

---

## 3. Chroma (Venice)

### A. 원본 의도판

**포지티브**
```
This is a photograph shot on Kodak Portra 400 film, a cinematic fashion editorial of a clearly adult East Asian woman in her late twenties with long straight black hair, a curvy healthy figure and a bright natural smile. She wears a fitted white button-down dress shirt, casually unbuttoned at the collar.

She sits casually on the front corner of a large dark mahogany executive desk, not behind it. Her torso leans slightly toward the camera. One knee is raised onto the desk while the other leg hangs down over the desk edge. An open silver laptop sits on the desk in the foreground, partially covering her lap. Her face is in the upper-middle of the vertical frame.

The room is an old-world private library: floor-to-ceiling shelves of antique books, heavy burgundy velvet curtains around a tall window behind her, a dark brown leather armchair, and a warm brass desk lamp on the desk.

Warm late-afternoon sunlight comes through the window behind and beside her, lighting her hair, face and white shirt, while the wooden room falls into deep, rich shadow. The lamp adds a faint tungsten glow. The camera is several meters away at eye level with an 85mm lens, mild telephoto compression and shallow depth of field, focused on her eyes. Visible film grain, gentle halation around the window, soft highlight roll-off. Her skin shows natural pores and slight asymmetry, with the same texture on face and body. Individual hair strands catch the backlight.
```

### B. 보정판

**포지티브**
```
This is a photograph shot on Kodak Portra 400 film, a cinematic fashion editorial of a clearly adult East Asian woman in her late twenties with long straight black hair, a curvy healthy figure and a bright natural smile. She wears a fitted white button-down dress shirt, casually unbuttoned at the collar.

She sits on the front corner of a large dark mahogany desk, her face turned toward the camera. Her right knee is raised and her right foot rests flat on the desk top, on the viewer's left. Her left leg hangs down over the front edge of the desk on the viewer's right, the foot relaxed in the air. Her right hand rests on top of her raised knee. Her left hand is flat on the desk beside her hip. Her torso leans slightly forward. The desk's front edge runs diagonally toward the camera on the viewer's right, and an open silver laptop sits on that nearer part of the desk, closer to the camera than she is, partially covering her hips.

The room is an old-world private library: floor-to-ceiling shelves of antique books, heavy burgundy velvet curtains, a dark brown leather armchair, and a warm brass desk lamp on the desk. A tall window is behind her on the viewer's left.

Warm late-afternoon sunlight from that window strikes her from behind and to the viewer's left, creating a bright rim light on her hair and shoulders and lighting the left side of her face as seen by the viewer. The other side of her face is in soft shadow, gently lifted by the warm glow of the brass lamp. The rest of the wooden room falls into deep shadow.

The camera is about five meters away at her chest height, at a front three-quarter angle, using an 85mm lens. The frame is vertical and shows her full body, the desk, the laptop and the bookshelves around her. Shallow depth of field, focus on her eyes. Visible film grain, gentle halation around the window, soft highlight roll-off. Her skin shows natural pores and slight asymmetry, with the same texture on her face, neck and hands.
```

**네거티브 (A·B 공통, 서술형)**
```
This image is a digital 3D render with airbrushed, plastic, waxy skin and an oversharpened, oversaturated, glossy look. It is an illustration or anime drawing. It is a collage with multiple panels, borders, text and watermarks. The anatomy is deformed, with extra fingers, extra limbs and twisted ankles. The perspective is distorted like a fisheye wide-angle lens.
```

**권장 설정**

| 항목 | 값 | 비고 |
|---|---|---|
| 비율 / 해상도 | 9:16, 720×1280 | |
| 스텝 | 10 (Venice 상한) | |
| CFG | 확인 안 됨. 조절할 수 있으면 기본값과 그보다 낮은 값을 비교 | Venice 구성이 저스텝이라 높은 CFG는 과포화를 부를 수 있어요 [판단] |
| 스타일 프리셋 / 프롬프트 향상 | 없음 / 끔 | |

**참고**

- 네거티브 입력란이 웹에 없거나 효과가 약하면, 피부·질감 문장을 Flash 판(§6)처럼 긍정형으로 바꿔요.
- 포지티브 첫 문장의 "This is a photograph"는 지우지 마세요. 애니로 기우는 걸 막아 줘요 [커뮤니티].

---

## 4. Anime (WAI) (Venice): 회화·일러스트판

실사 모델이 아니라서 "사진 질감" 지시는 전부 뺐고, 일러스트 화보로 바꿨어요. 좌우·손 지시는 태그로 표현이 어려워서 A·B를 나누지 않았어요.

**포지티브**
```
masterpiece, best quality, amazing quality, 1girl, solo, mature female, adult, east asian, black hair, long hair, straight hair, smile, looking at viewer, white shirt, collared shirt, open collar, sitting on desk, knee up, leaning forward, laptop, desk lamp, library, bookshelf, curtains, window, armchair, indoors, sunlight, backlighting, chiaroscuro, dark, depth of field, full body
```

**네거티브**
```
bad quality, worst quality, worst detail, sketch, censor, child, aged down, multiple views, extra digits
```

| 항목 | 값 | 근거 |
|---|---|---|
| 해상도 | 9:16, 720×1280 (16의 배수) | Venice API 제약 |
| 스텝 | 25~30 (Venice 상한 30) | [공식] 25~40 |
| CFG | 5~7 | [공식] |
| 샘플러 | Euler a (Venice에서 선택 가능한지는 확인 안 됨) | [공식] |

**참고**

- 제작자는 품질 태그와 네거티브를 길게 쓰지 말라고 명시해요. 위 수준이 상한이에요.
- 나이가 어려 보이면 로컬에서는 `(mature female:1.3)`처럼 가중치를 올리는 게 제작자 권장이에요. Venice에서 가중치가 먹는지는 확인 안 됨이라, `mature female`을 맨 앞으로 옮기는 방식이 대안이에요.

---

## 5. Z-Image Turbo (Venice, 참고용)

CFG 0인 증류 모델이라 네거티브가 효과 없어요. 그래서 회피 지시를 포지티브의 긍정형·부정형 문장으로 넣었어요. 언어 모델 인코더(Qwen3)라 "not a 3D render" 같은 부정 문장을 CLIP보다 잘 처리할 구조이긴 한데, 실제로 그런지는 확인 안 됨이에요.

**포지티브 (B 보정판 기반)**
```
This is a photograph shot on Kodak Portra 400 film, a cinematic fashion editorial of a clearly adult East Asian woman in her late twenties with long straight black hair, a curvy healthy figure and a bright natural smile. She wears a fitted white button-down dress shirt, casually unbuttoned at the collar.

She sits on the front corner of a large dark mahogany desk, her face turned toward the camera. Her right knee is raised and her right foot rests flat on the desk top, on the viewer's left. Her left leg hangs down over the front edge of the desk on the viewer's right, the foot relaxed in the air. Her right hand rests on top of her raised knee. Her left hand is flat on the desk beside her hip. Her torso leans slightly forward. The desk's front edge runs diagonally toward the camera on the viewer's right, and an open silver laptop sits on that nearer part of the desk, closer to the camera than she is, partially covering her hips.

The room is an old-world private library: floor-to-ceiling shelves of antique books, heavy burgundy velvet curtains, a dark brown leather armchair, and a warm brass desk lamp on the desk. A tall window is behind her on the viewer's left.

Warm late-afternoon sunlight from that window strikes her from behind and to the viewer's left, creating a bright rim light on her hair and shoulders and lighting the left side of her face as seen by the viewer. The other side of her face is in soft shadow, gently lifted by the warm glow of the brass lamp. The rest of the wooden room falls into deep shadow.

The camera is about five meters away at her chest height, at a front three-quarter angle, using an 85mm lens. The frame is vertical and shows her full body, the desk, the laptop and the bookshelves around her. Shallow depth of field, focus on her eyes. Visible film grain, gentle halation around the window, soft highlight roll-off. Her skin is natural and unretouched, with visible pores and slight asymmetry, and the same texture on her face, neck and hands. This is one single uncut photograph, not a 3D render, not an illustration.
```

| 항목 | 값 |
|---|---|
| 네거티브 | 비움 |
| 스텝 | 8 (고정) |
| 비율 | 9:16 |

참고로 무검열 표시가 없는 모델이라 노출 장면에는 맞지 않을 수 있어요.

## 6. Venice SD35 (참고용)

1,500자 제한이라 **Chroma A 포지티브(1,456자)를 그대로** 쓸 수 있어요. CLIP 77토큰 + T5 조합이라 앞 문장의 비중이 커요. 네거티브는 Lustify 네거티브를 쓰면 돼요. 공식 예시 기준은 28스텝, CFG 3.5~4.5예요(Venice 상한 30스텝).

---

## 7. 로컬 Chroma1-HD (원본)

프롬프트는 **§3 Chroma B 포지티브와 서술형 네거티브를 그대로** 써요.

| 항목 | 값 | 근거 |
|---|---|---|
| 해상도 | 768×1344 (약 1MP, 9:16에 가까움) | 공식 예시 1152×1152(약 1.3MP) [판단] |
| 스텝 | 26 | 공식 ComfyUI 워크플로 |
| CFG | 3.8 (diffusers 예시는 3.0) | 공식 |
| 샘플러 / 스케줄러 | euler / beta (α 0.45, β 0.45) | 공식 워크플로 |
| ModelSamplingAuraFlow shift | 1.0 | 공식 워크플로 메모: "제작자가 의도한 값, 디테일이 더 좋음" |
| T5TokenizerOptions min_padding | 1 | 공식 워크플로 메모: "1이 공식, 0도 동작" |
| 텍스트 인코더 | t5xxl fp16 또는 flan-t5-xxl (정밀도 우선이면 Q8 GGUF) | 공식 워크플로 메모 |

양자화 선택과 ControlNet·디테일러 조합은 로컬 환경 정보를 받은 뒤 확정할게요.

## 8. 로컬 Chroma Flash

CFG 1이라 네거티브가 계산되지 않아요. 그래서 조명 문단을 줄이고(과노출 경향), 회피 지시를 긍정형으로 바꿨어요.

**포지티브**
```
This is a photograph shot on Kodak Portra 400 film, a cinematic fashion editorial of a clearly adult East Asian woman in her late twenties with long straight black hair, a curvy healthy figure and a bright natural smile. She wears a fitted white button-down dress shirt, casually unbuttoned at the collar.

She sits on the front corner of a large dark mahogany desk, her face turned toward the camera. Her right knee is raised and her right foot rests flat on the desk top, on the viewer's left. Her left leg hangs down over the front edge of the desk on the viewer's right, the foot relaxed in the air. Her right hand rests on top of her raised knee. Her left hand is flat on the desk beside her hip. Her torso leans slightly forward. The desk's front edge runs diagonally toward the camera on the viewer's right, and an open silver laptop sits on that nearer part of the desk, closer to the camera than she is, partially covering her hips.

The room is an old-world private library: floor-to-ceiling shelves of antique books, heavy burgundy velvet curtains, a dark brown leather armchair, and a warm brass desk lamp on the desk. A tall window is behind her on the viewer's left.

Late-afternoon sunlight from that window comes from behind her on the viewer's left, putting a warm rim of light on her hair and shoulders. The other side of her face is in soft shadow with a faint warm glow from the brass lamp.

The camera is about five meters away at her chest height, at a front three-quarter angle, using an 85mm lens. The frame is vertical and shows her full body, the desk, the laptop and the bookshelves around her. Shallow depth of field, focus on her eyes. Visible film grain, gentle halation around the window, soft highlight roll-off. Her skin is natural and unretouched, with visible pores and slight asymmetry, and the same texture on her face, neck and hands. One single photograph, unedited.
```

| 항목 | 값 | 근거 |
|---|---|---|
| 네거티브 | 비움. 꼭 필요하면 NAG 노드로 위 서술형 네거티브를 적용 | ComfyUI 코드 / NAG |
| CFG | 1.0 (정확히) | [커뮤니티] |
| 스텝 | 8~12 | [커뮤니티] 8 / 10 이상 |
| 샘플러 / 스케줄러 | heun / beta | [커뮤니티] |
| 해상도 | 768×1344 | |

**참고:** 결과가 과하게 밝거나 하이라이트가 날아가면 조명 문장을 더 줄여요. "warm rim of light" 한 구만 남기는 식이에요 [커뮤니티 보고 기반 판단].
