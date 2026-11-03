# 02. 장면 확장: 체크리스트, 소나기 샘플, 언어 모델에 맡기는 방법

## 1. 왜 사람이 대신 해야 하나

- **GPT 쪽:** OpenAI는 DALL-E 3 논문(2023)에서 짧은 요청을 언어 모델이 길고 자세한 묘사로 다시 쓰는 방식(caption upsampling)을 설명했어요. 학습 때 쓴 긴 캡션과 추론 때 입력의 분포를 맞추려는 목적이에요. 논문 원문은 이 세션에서 열지 못해서 2차 자료로 확인했어요. 지금의 GPT 이미지 생성도 같은 구조인지는 확인 안 됨이지만, "소나기"만 써도 결과가 다 채워지는 현상과 들어맞아요 [판단].
- **Venice·로컬 쪽:** Lustify·WAI는 CLIP만 쓰고, Chroma는 T5만 써요. 둘 다 언어 모델처럼 "그 상황이면 이런 결과가 생긴다"를 추론하는 단계가 없어요. 쓴 단어가 학습 데이터에서 함께 나오던 시각 요소만 끌어와요 [판단]. "rain"이 학습 캡션에서 주로 빗줄기 배경과 함께 나왔다면, 젖은 머리카락은 따로 써 줘야 나와요.
- **Venice 프롬프트 향상:** 확장은 해 주지만 구도·조명·분위기를 자기 판단으로 채워 넣어요 [공식]. 아래 규칙처럼 "물리적 결과만" 넣도록 제한할 수 없어요.

---

## 2. 확장 원칙: 무엇을 넣고 무엇을 빼나

확장 후보마다 아래 네 가지 검사를 거쳐요. 하나라도 통과하지 못하면 넣지 않아요.

| 검사 | 질문 | 통과 예 (소나기) | 탈락 예 (소나기) |
|---|---|---|---|
| **① 인과** | 입력한 상황에서 물리적으로 반드시, 또는 거의 반드시 생기는가? | 젖은 바닥의 반사, 젖어서 달라붙은 머리카락 | 무지개 (조건이 맞을 때만 생김), 번개 |
| **② 비추가** | 새 물체·의상·인물·소품·분위기 형용사를 만들지 않는가? 상황 자체의 물질(빗물, 물방울, 웅덩이)은 결과라서 허용해요 | 웅덩이, 처마 끝 물방울 | 우산, 우비, 지나가는 행인, 네온 간판, "melancholic" |
| **③ 가시성** | 지정한 구도·거리·초점에서 실제로 보이는가? | 전신 구도에서 바닥 웅덩이 | 전신 구도에서 속눈썹의 물방울 (클로즈업일 때만) |
| **④ 충돌** | 기존 지시와 물리적으로 부딪치지 않는가? 부딪치면 넣지 말고 **사용자에게 질문** | 흐린 하늘 ↔ (입력에 다른 광원 지시 없음) | 소나기 ↔ "황금빛 오후 햇살" → 질문 대상 |

### 강도·경과 시간·노출 정도 (확장 전에 정하는 세 가지)

같은 "소나기"라도 이 세 가지에 따라 결과가 달라져요. 입력에 없으면 단어의 사전적 기본값을 쓰고, **가정했다는 사실을 표시**해요.

| 변수 | 선택지 | 결과 차이 |
|---|---|---|
| 강도 | 이슬비 / 비 / 소나기·폭우 | 빗줄기 굵기, 웅덩이 파문 크기, 튀는 물, 원경이 흐려지는 정도 |
| 경과 시간 | 막 시작 / 몇 분 / 한참 | 옷과 머리가 얼룩지게 젖음 → 완전히 젖음, 웅덩이 유무 |
| 노출 정도 | 그대로 맞음 / 처마·실내에서 봄 | 인물 변화의 유무. 실내라면 인물은 마른 상태이고 창문에만 변화가 생김 |

---

## 3. 장면 확장 체크리스트

상황 하나를 받으면 아래 표를 위에서부터 채워요. 각 칸에는 "결과 + 왜 생기는지"를 한 줄로 써요. 이유를 같이 써야 ① 인과 검사를 스스로 할 수 있어요.

### A. 인물에게 생기는 변화

| 항목 | 확인할 것 |
|---|---|
| 피부 | 물·땀·기름·온도로 인한 표면 변화(물방울, 광택, 홍조, 소름). 부위별 차이(이마·코·쇄골·팔뚝) |
| 머리카락 | 젖음·바람·정전기·습기로 인한 형태 변화(뭉침, 달라붙음, 잔머리, 끝에서 떨어지는 물) |
| 옷 | 재질별 반응(면은 진해지고 비침, 두꺼운 원단은 무거워져 처짐), 몸에 달라붙는 부위, 주름 형태 변화 |
| 표정·자세 | **물리적 반사작용만**(눈부심에 눈을 가늘게 뜸 등). 사용자가 표정·자세를 지정했다면 그대로 두고 바꾸지 않아요 |

### B. 주변 환경에 생기는 변화

| 항목 | 확인할 것 |
|---|---|
| 바닥 | 젖음, 광택, 웅덩이, 파문, 튀는 물, 쌓임(눈·낙엽은 입력에 있을 때만) |
| 벽·사물 표면 | 젖은 면의 색 변화, 흘러내리는 물줄기, 모서리·끝에 맺힌 물방울. **입력에 있는 사물만** 대상이에요 |
| 공기 | 빗줄기, 물보라, 김, 먼지, 열 아지랑이, 원경이 흐려지는 정도 |

### C. 빛에 생기는 변화

| 항목 | 확인할 것 |
|---|---|
| 광원 | 주 광원의 종류와 방향(직사광 / 흐린 하늘의 확산광 / 인공광) |
| 그림자 | 그림자의 진하기와 경계(직사광이면 짙고 날카로움, 확산광이면 옅고 부드러움) |
| 반사 | 젖은 면·물·유리에 비치는 상(광원, 하늘, 인물) |
| 색온도와 대비 | 차가움·따뜻함, 전체 대비의 높낮이 |

### D. 화면 깊이별 요소

| 깊이 | 확인할 것 |
|---|---|
| 전경 (카메라와 인물 사이) | 카메라 가까이 있어서 초점이 나간 요소(빗방울, 물보라, 김) |
| 중경 (인물) | 인물 주변에서 초점이 맞는 상황 요소(어깨에 떨어지는 빗방울, 튀는 물) |
| 배경 | 대기 원근(멀수록 흐리고 대비가 낮음), 겹쳐 보이는 빗줄기 |

### E. 카메라에 생기는 변화

| 항목 | 조건 |
|---|---|
| 렌즈에 맺힌 물방울 | **촬영자도 비를 맞는 위치일 때만.** 처마 아래나 실내에서 찍으면 넣지 않아요 |
| 김 서림 | 온도·습도 차이가 클 때만(추운 밖에서 따뜻한 실내로, 뜨거운 탕) |
| 빗줄기의 모양 | 셔터 속도 지시가 있으면 따라가요(빠르면 정지된 방울, 느리면 줄무늬). 없으면 넣지 않아요 |
| 초점 | 전경 요소가 앞초점으로 흐려지는지 |

### F. 넣지 않는 것

소리, 냄새, 온도감 같은 보이지 않는 감각. 감정·분위기 형용사(`moody`, `melancholic`, `romantic`). 시간 전후 이야기(방금 뛰어왔다 등). 사용자가 쓰지 않은 소품·의상·인물·간판·차량.

### G. 모델별 출력 분량

| 대상 모델 | 넣을 항목 수 | 형태 |
|---|---|---|
| GPT, Chroma, Z-Image | 8~12개 | 문장. 인물 → 환경 → 빛 → 깊이 → 카메라 순서 |
| Lustify, SDXL 계열 | 4~6개 | 짧은 태그. 화면에서 면적이 큰 것부터(젖은 머리·옷 → 바닥 반사 → 흐린 빛) |
| WAI | 3~5개 | Danbooru 태그(`wet hair`, `wet clothes`, `rain`, `puddle`, `overcast`) |

---

## 4. 소나기 확장 샘플

### 입력

> 흰 면 셔츠를 입은 긴 생머리 성인 여성이 낮에 도심 거리 인도에 서 있다. 소나기. 전신, 눈높이, 50mm.

### 확장 전에 한 가정

- **강도:** "소나기"의 기본값으로, 갑자기 쏟아지는 굵은 비예요.
- **경과 시간:** 몇 분 이상 맞아서 머리와 옷이 다 젖은 상태로 가정했어요. 막 시작한 순간을 원하면 A 항목을 "얼룩지게 젖음"으로 바꿔야 해요.
- **노출 정도:** 입력에 우산이나 처마가 없으니 그대로 맞는 것으로 봤어요.
- **촬영자 위치:** 같은 거리에서 비를 맞으며 찍는다고 가정했어요. 렌즈 물방울(E)은 이 가정에 달려 있어요.

### 체크리스트 적용 결과

| 분류 | 결과 | 이유 |
|---|---|---|
| A 피부 | 얼굴·목·쇄골·팔뚝에 맺힌 작은 물방울, 젖은 피부의 은은한 광택 | 빗물이 피부 표면에 맺힘 |
| A 머리카락 | 흠뻑 젖어 굵은 가닥으로 뭉침, 이마·뺨·목에 달라붙음, 머리끝에서 물이 떨어짐 | 물이 머리카락을 묶고 무겁게 함 |
| A 옷 | 흰 면 셔츠가 젖어 반투명해지고 어깨·팔·몸통에 달라붙음, 주름이 늘어지지 않고 몸을 따라 붙음 | 면은 물을 흡수하면 비치고 무거워짐 |
| A 표정 | 입력에 표정 지시가 없으므로 **반사작용 하나만**: 얼굴에 떨어지는 비 때문에 눈을 살짝 가늘게 뜸. 원하지 않으면 빼요 | 반사작용 (선택 항목) |
| B 바닥 | 젖어서 어두워지고 광택이 도는 보도, 얕은 웅덩이에 빗방울 파문, 발 주변에 튀는 물 | 굵은 비가 몇 분 이상 내림 |
| B 표면 | 길가 벽면이 젖어 색이 진해짐 | 입력의 "도심 거리"에 포함된 표면만. 새 사물은 넣지 않음 |
| B 공기 | 화면 전체에 보이는 빗줄기, 지면 가까이 낮게 깔린 물보라 | 굵은 빗방울이 지면에 부딪힘 |
| C 광원 | 두꺼운 구름 아래의 확산광, 직사광 없음 | 소나기구름이 해를 가림 |
| C 그림자 | 거의 없음, 발밑에만 옅고 부드러운 그림자 | 확산광 |
| C 반사 | 젖은 보도에 인물의 흐릿한 반영과 밝은 하늘 반사 | 젖은 면이 거울처럼 작동 |
| C 색온도·대비 | 차갑고 약간 회청색, 낮은 대비 | 흐린 날의 하늘빛 |
| D 전경 | 렌즈 가까이 떨어지는 빗방울이 초점 밖에서 흐린 줄로 보임 | 50mm, 인물에 초점 |
| D 배경 | 거리 끝으로 갈수록 빗줄기가 겹쳐 뿌옇고 대비가 낮아짐 | 대기 중 물방울로 인한 산란 |
| E 렌즈 | 렌즈 앞면에 맺힌 물방울 몇 개, 해당 부분이 부드럽게 번짐 (가정에 의존) | 촬영자도 비를 맞음 |
| **넣지 않은 것** | 우산, 우비, 행인, 택시, 네온 간판, 가로등 불빛, 번개, 무지개, "우울한 분위기", 추위로 떠는 자세 | ② 비추가 / ① 인과 탈락 |

### 출력 예시: Chroma·GPT용 문장형

```
This is a photograph of an adult woman in a white cotton shirt with long straight hair, standing on a city sidewalk in the daytime during a sudden heavy rain shower. Full body, eye-level, 50mm lens.

Her hair is completely soaked, hanging in heavy clumped strands that cling to her forehead, cheeks and neck, with water dripping from the ends. Small water droplets bead on her face, neck, collarbones and forearms, and her wet skin has a soft sheen. The soaked white cotton shirt has turned semi-translucent and clings to her shoulders, arms and torso.

The sidewalk is dark and glossy with water. Shallow puddles around her feet are broken by the impact rings of raindrops, and water splashes up around her shoes. The wall beside the sidewalk is darkened by rain. Rain streaks fill the whole frame, with low spray hovering just above the ground.

The light is soft and diffused under a thick overcast sky, with no direct sunlight and only faint, soft shadows under her feet. The wet pavement reflects a blurred image of her and the pale sky. Colors are cool and slightly blue-grey, with low contrast.

Raindrops falling close to the lens appear as out-of-focus streaks in the foreground. Toward the end of the street, overlapping rain makes the background hazy and low in contrast. A few water droplets sit on the front of the lens, softly blurring parts of the image.
```

### 출력 예시: Lustify·SDXL용 태그형

```
photograph, adult woman, white cotton shirt, standing on city sidewalk, heavy rain, soaked hair, wet hair clinging to face, wet see-through shirt, water droplets on skin, wet glossy pavement, puddles with ripples, reflection on wet ground, overcast, soft diffused light, cool tones, rain streaks, full body
```

### 같은 소나기를 기존 서재 프롬프트에 넣으면 (충돌 검사 예)

입력이 "서재 화보 + 창밖 소나기"라면 확장 결과가 이렇게 달라져요.

- **인물 변화 없음.** 실내에 있으니 A 항목은 전부 비어요.
- **창 유리:** 바깥면을 타고 흘러내리는 빗물, 맺힌 물방울. 바깥 풍경은 흐릿한 회색으로 보여요.
- **빛:** 창으로 들어오는 빛이 흐린 회청색 확산광이 돼요.
- **충돌:** 원본의 "따뜻한 늦은 오후 황금빛 햇살이 창으로 들어온다"와 정면으로 부딪쳐요. 해가 비치면서 비가 오는 여우비도 물리적으로 가능하지만 드문 상황이에요. 그래서 확장 단계에서 임의로 고르지 않고 질문해요. "① 햇살을 빼고 흐린 빛 + 램프 위주로 갈지 ② 여우비로 해서 햇살을 유지할지"

---

## 5. 다른 상황 간단 적용 (젖은 셔츠, 역광, 수영장)

| 상황 | 인물 | 환경 | 빛 | 깊이·카메라 | 대표적인 탈락 항목 |
|---|---|---|---|---|---|
| **젖은 셔츠** (원인 미지정) | 셔츠가 반투명해지고 피부에 달라붙음, 젖은 부위는 색이 진해지고 마른 부위와 경계가 생김. **원인이 없으면 머리·피부가 젖었는지는 정하지 않고 질문해요** (비? 물놀이? 물을 쏟음?) | 원인에 따라 다름 | 젖은 원단의 은은한 광택 | 해당 없음 | 땀, 비, 수영장 (원인을 지어내지 않음) |
| **역광** | 머리카락 가장자리의 밝은 테두리(림 라이트), 잔머리·솜털이 빛남, 얼굴 앞면은 상대적으로 어두움, 얇은 원단은 빛이 비침 | 바닥에 카메라 쪽으로 길게 늘어진 그림자 | 광원이 인물 뒤에 있음, 대비가 큼. 광원이 화면 안이면 하이라이트가 날아감 | 렌즈 플레어·베일링 글레어(광원이 화면 안이나 가장자리일 때), 대비 저하 | 반사판, 보조 조명 (지시가 없으면 넣지 않음. 얼굴을 밝히고 싶으면 사용자에게 질문) |
| **수영장** (물속에 있다고 할 때) | 젖은 머리, 피부의 물방울, 물 높이에 맞춘 수면선 | 수면의 잔물결, 몸 주변의 파문 | 바닥에 일렁이는 빛 무늬(코스틱), 수면 반사, 물속 몸은 굴절로 짧아 보이고 청록색으로 물듦 | 수면 반사로 물속이 덜 보임 | 튜브, 선베드, 다른 사람, 칵테일 (수영장에 흔하지만 입력에 없음) |

---

## 6. 이 확장을 언어 모델(AI 채팅)에 맡기는 방법

### 효과가 있나

- **효과 있음 쪽 근거:**
  - DALL-E 3 논문(2차 자료): 언어 모델로 짧은 프롬프트를 긴 묘사로 다시 쓰는 것이 결과를 개선해요.
  - Venice 공식 문서: 짧은 프롬프트에서는 향상 기능이 결과를 더 자세하고 일관되게 만든다고 해요.
  - Z-Image 공식 카드: 별도 Prompt Enhancer가 "표면 묘사를 넘어 세계 지식을 활용하는 추론 능력"을 준다고 설명해요.
- **위험 쪽 근거:** DALL-E 3 방식을 오픈소스로 재현한 예시가 소품과 분위기를 지어내요. "흰 샌드위치"에 소스·피클 병과 "아늑한 부엌"이 붙고, "흰 차와 빨간 양"에 "버려진 차, 깨진 창문, 섬뜩한 분위기"가 붙어요. 언어 모델은 제한하지 않으면 "그럴듯한 장면"을 만들려고 해요.
- **결론 [판단]:** 맡기는 건 효과적이에요. 다만 **"물리적 결과만, 이유를 적게, 충돌은 질문"**이라는 제약을 시스템 지시로 고정하고, 결과를 표로 받아서 사람이 한 번 걸러야 해요. Venice 프롬프트 향상처럼 제약을 줄 수 없는 도구는 이 목적에 맞지 않아요.

### 권장 흐름 (2단계)

1. **확장 단계:** 언어 모델이 체크리스트 표(결과 + 이유 + 검사 통과 여부)를 만들어요. 가정한 것과 질문할 것을 따로 적어요.
2. **사람이 확인:** 탈락시킬 항목과 질문에 대한 답을 정해요.
3. **조립 단계:** 승인된 항목만으로 대상 모델 형식(문장형 / 태그형, 길이 예산)의 최종 프롬프트를 만들어요.

한 번에 최종 프롬프트까지 받으면 지어낸 항목이 섞여도 눈에 잘 안 띄어요. 표를 거치면 "이유" 칸에서 걸러져요.

### 시스템 지시 템플릿 (복사해서 사용)

언어 모델은 영어 지시를 더 일관되게 따르는 편이라 지시문은 영어로 썼어요. 대화는 한국어로 해도 돼요.

```
You are a scene-consequence expander for image-generation prompts.

INPUT: a base scene description (subject, wardrobe, location, composition, camera) and one or more SITUATIONS (e.g. "sudden rain shower", "wet shirt", "backlight", "swimming pool").

YOUR JOB: list only the PHYSICAL CONSEQUENCES that the situation produces in the given scene, so that an image model that cannot reason can draw them.

HARD RULES
1. Causality: include an item only if it follows physically and almost unavoidably from the stated situation. Conditional effects (rainbows, lightning, lens flare without a light source in frame) are excluded unless the input states the condition.
2. No additions: never introduce objects, props, clothing, people, vehicles, signs, animals, light sources, or mood/emotion adjectives that the input did not mention. Materials that ARE the consequence (water drops, puddles, steam, spray) are allowed.
3. Visibility: include an item only if it is visible at the stated framing, distance and focus. Close-up-only details are dropped for full-body shots.
4. Conflicts: if a consequence contradicts an existing instruction (e.g. overcast rain vs. golden sunlight), do NOT resolve it yourself. List it under QUESTIONS with the options.
5. Do not change pose, expression, wardrobe, or camera settings that the user specified. Physical reflexes (squinting at rain) may be listed as OPTIONAL only if the user gave no expression.
6. Unknown intensity, duration, or exposure: state the assumption you used under ASSUMPTIONS, choosing the plain dictionary default of the situation word.

OUTPUT FORMAT (stage 1)
ASSUMPTIONS: bullet list
TABLE with columns: Category (Person-skin / Person-hair / Person-clothing / Person-reflex / Ground / Surfaces / Air / Light-source / Shadows / Reflections / Color-contrast / Foreground / Background / Camera) | Consequence | Physical reason | Optional? (yes/no)
EXCLUDED: things a typical image of this situation would show but that fail the rules, with the rule number
QUESTIONS: conflicts that need the user's decision

Wait for the user's approval. Then, when asked, compile ONLY the approved rows into the requested target format:
- "sentence" target: natural English paragraphs, order person > environment > light > depth > camera, under {TOKEN_BUDGET} tokens, no headings, no capitals for emphasis, no "do not" sentences.
- "tag" target: comma-separated short tags, largest visible effects first, at most {TAG_COUNT} tags.
```

### 사용 팁

- **대상 모델과 길이 예산을 같이 줘요.** 예: `target: tag, TAG_COUNT: 6` (Lustify), `target: sentence, TOKEN_BUDGET: 200` (Chroma에서 확장 부분에 쓸 몫).
- **이유 칸이 애매한 행은 지워요.** "흔히 그렇다", "분위기상"은 인과가 아니라 연상이에요.
- **성인 콘텐츠 검열:** 확장 단계는 대부분 날씨·빛·재질 묘사라 일반 언어 모델에서도 거절될 일이 적어요. 누드 장면이면 신체 묘사를 "피부에 맺힌 물방울"처럼 물리적 결과로만 다루게 하면 돼요. 그래도 거절되면 Venice의 무검열 텍스트 모델을 쓰는 방법이 있어요(변경 기록에 Venice Uncensored 모델이 있어요). 어느 쪽이든 미성년자로 보일 수 있는 묘사는 확장 대상에서 빠지도록 기본 장면에 "adult, late 20s"를 고정해 두는 게 안전해요.
- **Venice 프롬프트 향상과 같이 쓰지 않아요.** 직접 확장한 프롬프트를 향상 기능이 다시 고쳐 쓰면 통제가 사라져요.
