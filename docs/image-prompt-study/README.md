# 이미지 생성 프롬프트·설정 조사 (Venice 웹 / 로컬 Chroma)

조사일: 2026-11-03
목표: GPT 이미지 생성 결과에 최대한 가깝게, Venice 무검열 모델과 로컬 Chroma로 실사풍 성인 인물 화보를 만드는 방법 찾기

## 문서 구성

| 파일 | 내용 | 요청 항목 |
|---|---|---|
| [01-models.md](01-models.md) | 모델별 비교표, Venice 웹 기능, 모델별 프롬프트 규칙 | 결과 1, 2 |
| [02-scene-expansion.md](02-scene-expansion.md) | 장면 확장 체크리스트, 소나기 샘플, 언어 모델에 맡기는 지시문 | 결과 3 |
| [03-conversions.md](03-conversions.md) | 테스트 GPT 프롬프트 변환 예시 (원본 의도판 / 보정판) | 결과 4 |
| [04-closing-the-gap.md](04-closing-the-gap.md) | GPT에 가깝게 만드는 방법, 보완 도구, 목적별 추천 | 결과 5, 6 |

## 출처 표기 규칙

- **[공식]** Venice 공식 문서·API·변경 기록, 모델 제작자의 Hugging Face/Civitai 페이지, 공식 저장소(코드)
- **[제작자 샘플]** 제작자가 올린 예시 이미지의 생성 메타데이터. 명시적 권장값은 아니지만 제작자가 실제로 쓴 값
- **[커뮤니티]** 제3자 모델 카드, 블로그, 리뷰
- **[판단]** 위 자료를 근거로 한 이 문서의 해석. 직접 생성 테스트는 하지 않았어요
- **확인 안 됨** 근거를 찾지 못한 항목. 추측으로 채우지 않았어요

## 조사 범위의 한계

- Venice 계정 접속, 프롬프트 입력, 이미지 생성은 하지 않았어요. 웹 UI 화면은 직접 보지 못했고, 공식 문서·공개 모델 목록 API(`GET /models?type=image`, 인증 불필요)·변경 기록으로만 확인했어요.
- Reddit은 자동 접근이 막혀 있어서 직접 읽지 못했어요. 커뮤니티 자료는 Hugging Face 커뮤니티 모델 카드와 웹 검색 요약 위주예요.
- OpenAI DALL-E 3 논문 PDF(cdn.openai.com)는 네트워크 정책 때문에 열지 못했어요. 해당 내용은 2차 자료로 표시했어요.
- 직접 생성 테스트를 하지 않아서 "어느 쪽이 더 낫다"는 비교는 전부 **[판단]**이에요. 실제 결과로 검증이 필요해요.

## 로컬 환경 정보가 필요한 항목 (답변 대기)

아래는 로컬 실행 환경을 알려 주시면 확정할게요. 지금 문서에는 환경과 무관한 공통 내용만 들어 있어요.

1. **UI:** ComfyUI / Forge 계열 / SwarmUI / 기타. Chroma 공식 워크플로는 ComfyUI 기준이고, NAG·디테일러·ControlNet 같은 보완 도구도 ComfyUI 커스텀 노드가 중심이에요.
2. **GPU와 메모리:** GPU 모델과 VRAM, 시스템 RAM. 양자화 선택(01-models.md §4)이 여기에 달려 있어요.
3. **이미 받은 파일:** Chroma 파일명(HD / Base / Flash, 양자화 종류)과 T5 텍스트 인코더 파일명.

## 주요 발견 요약

1. **원본 GPT 프롬프트는 그대로 쓸 수 없어요.** 3,563자이고 CLIP 기준 688토큰, T5 기준 815토큰이에요. Venice의 Lustify·WAI 입력 제한은 1,500자이고, Chroma의 T5 인코더는 최대 길이 512토큰으로 설정돼 있어요. 줄이는 과정이 변환의 핵심이에요.
2. **Venice의 Chroma는 스텝 상한이 10이에요.** 공개 모델 목록 API에서 `steps: {default: 10, max: 10}`으로 나와요. 공식 Chroma1-HD 워크플로(26스텝, CFG 3.8)와는 다른 저스텝 구성으로 보이는데, 어떤 방식인지(Flash 계열 적용 여부)는 확인 안 됨이에요.
3. **"Lustify v8"은 Civitai의 LUSTIFY! APEX (V8)이에요.** SDXL 1.0 기반이고, Venice 등록일은 2026-03-30이에요. 제작자 샘플은 DPM++ 2M SDE Karras, 30스텝, CFG 3.5~4이고, 태그 위주에 자연어를 섞은 프롬프트예요.
4. **Venice 프롬프트 향상(마법봉)은 장면 확장을 해 주지만 의도도 바꿔요.** 공식 문서에 따르면 구도·조명·분위기를 채워 넣고, 긴 프롬프트에는 꺼 두는 편이 제어가 낫다고 해요. 스타일 프리셋도 프롬프트에 텍스트로 펼쳐 넣는 방식이라 글자 수 제한을 같이 써요.
5. **CFG 1에서는 네거티브 프롬프트가 아예 계산되지 않아요.** ComfyUI 코드 기준이고, Chroma Flash를 쓸 때 해당돼요. 네거티브가 필요하면 NAG 같은 별도 방식을 써야 해요.

## 주요 출처 목록

- Venice 공개 모델 목록 API: `https://api.venice.ai/api/v1/models?type=image` (2026-11-03 조회)
- Venice 문서: [Image Generation](https://docs.venice.ai/guides/media/image-generation), [Prompt Enhancement](https://docs.venice.ai/guides/media/prompt-enhancement), [Image Editing](https://docs.venice.ai/guides/media/image-editing), [Image Upscaling](https://docs.venice.ai/guides/media/image-upscaling), [Generate API reference](https://docs.venice.ai/api-reference/endpoint/image/generate), [Image Models](https://docs.venice.ai/models/image), [FAQ](https://venice.ai/faqs)
- Venice 변경 기록: [venice.ai/changelog](https://venice.ai/changelog) (2026-10까지), [이전 변경 기록](https://veniceai.featurebase.app/changelog) (~2026-09)
- Lustify: [Civitai 573152](https://civitai.com/models/573152) (API로 버전 설명·샘플 메타데이터 조회)
- WAI: [Civitai 827184](https://civitai.com/models/827184)
- Chroma: [Chroma1-HD](https://huggingface.co/lodestones/Chroma1-HD), [Chroma1-Flash](https://huggingface.co/lodestones/Chroma1-Flash), [Chroma (구 저장소)](https://huggingface.co/lodestones/Chroma), [Civitai 1330309](https://civitai.com/models/1330309), 공식 ComfyUI 워크플로 JSON
- Z-Image Turbo: [Tongyi-MAI/Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo)
- SD3.5 Large: [stabilityai/stable-diffusion-3.5-large](https://huggingface.co/stabilityai/stable-diffusion-3.5-large)
- ComfyUI 코드: [comfy/samplers.py](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py), [comfy/sd1_clip.py](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/sd1_clip.py), [comfy/text_encoders](https://github.com/comfyanonymous/ComfyUI/tree/master/comfy/text_encoders)
- [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF), [Normalized Attention Guidance](https://github.com/ChenDarYen/Normalized-Attention-Guidance)
- 커뮤니티 모델 카드: [andriadze/Chroma1-Flash](https://huggingface.co/andriadze/Chroma1-Flash), [darian23/Chroma1-Flash-LoRA](https://huggingface.co/darian23/Chroma1-Flash-LoRA), [silveroxides/Chroma1-HD-GGUF](https://huggingface.co/silveroxides/Chroma1-HD-GGUF), [silveroxides/Chroma1-HD-fp8-scaled](https://huggingface.co/silveroxides/Chroma1-HD-fp8-scaled), [tonera/Chroma1-HD-SVDQ](https://huggingface.co/tonera/Chroma1-HD-SVDQ)
- 캡션 업샘플링(DALL-E 3 방식 재현): [sayakpaul/caption-upsampling](https://github.com/sayakpaul/caption-upsampling)
