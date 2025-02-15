from typing import Dict, List, Literal, TypedDict

from facefusion.typing import AudioFrame, Face, FaceSet, StateContext, VisionFrame

AgeModifierModel = Literal['styleganex_age']
FaceDebuggerItem = Literal['bounding-box', 'face-landmark-5', 'face-landmark-5/68', 'face-landmark-68', 'face-landmark-68/5', 'face-mask', 'face-detector-score', 'face-landmarker-score', 'age', 'gender']
FaceEnhancerModel = Literal['codeformer', 'gfpgan_1.2', 'gfpgan_1.3', 'gfpgan_1.4', 'gpen_bfr_256', 'gpen_bfr_512', 'gpen_bfr_1024', 'gpen_bfr_2048', 'restoreformer_plus_plus']
FaceSwapperModel = Literal['blendswap_256', 'ghost_256_unet_1', 'ghost_256_unet_2', 'ghost_256_unet_3', 'inswapper_128', 'inswapper_128_fp16', 'simswap_256', 'simswap_512_unofficial', 'uniface_256']
FrameColorizerModel = Literal['ddcolor', 'ddcolor_artistic', 'deoldify', 'deoldify_artistic', 'deoldify_stable']
FrameEnhancerModel = Literal['clear_reality_x4', 'lsdir_x4', 'nomos8k_sc_x4', 'real_esrgan_x2', 'real_esrgan_x2_fp16', 'real_esrgan_x4', 'real_esrgan_x4_fp16', 'real_hatgan_x4', 'real_esrgan_x8', 'real_esrgan_x8_fp16', 'span_kendata_x4', 'ultra_sharp_x4']
LipSyncerModel = Literal['wav2lip', 'wav2lip_gan']

FaceSwapperSet = Dict[FaceSwapperModel, List[str]]

AgeModifierInputs = TypedDict('AgeModifierInputs',
{
	'reference_faces' : FaceSet,
	'target_vision_frame' : VisionFrame
})
FaceDebuggerInputs = TypedDict('FaceDebuggerInputs',
{
	'reference_faces' : FaceSet,
	'target_vision_frame' : VisionFrame
})
FaceEnhancerInputs = TypedDict('FaceEnhancerInputs',
{
	'reference_faces' : FaceSet,
	'target_vision_frame' : VisionFrame
})
FaceSwapperInputs = TypedDict('FaceSwapperInputs',
{
	'reference_faces' : FaceSet,
	'source_face' : Face,
	'target_vision_frame' : VisionFrame
})
FrameColorizerInputs = TypedDict('FrameColorizerInputs',
{
	'target_vision_frame' : VisionFrame
})
FrameEnhancerInputs = TypedDict('FrameEnhancerInputs',
{
	'target_vision_frame' : VisionFrame
})
LipSyncerInputs = TypedDict('LipSyncerInputs',
{
	'reference_faces' : FaceSet,
	'source_audio_frame' : AudioFrame,
	'target_vision_frame' : VisionFrame
})

FrameProcessorStateKey = Literal\
[
	'age_modifier_model',
	'age_modifier_direction',
	'face_debugger_items',
	'face_enhancer_model',
	'face_enhancer_blend',
	'face_swapper_model',
	'face_swapper_pixel_boost',
	'face_swapper_expression_restorer',
	'frame_colorizer_model',
	'frame_colorizer_blend',
	'frame_colorizer_size',
	'frame_enhancer_model',
	'frame_enhancer_blend',
	'lip_syncer_model'
]
FrameProcessorState = TypedDict('FrameProcessorState',
{
	'age_modifier_model': AgeModifierModel,
	'age_modifier_direction': int,
	'face_debugger_items' : List[FaceDebuggerItem],
	'face_enhancer_model' : FaceEnhancerModel,
	'face_enhancer_blend' : int,
	'face_swapper_model' : FaceSwapperModel,
	'face_swapper_pixel_boost' : str,
	'frame_colorizer_model' : FrameColorizerModel,
	'frame_colorizer_blend' : int,
	'frame_colorizer_size' : str,
	'frame_enhancer_model' : FrameEnhancerModel,
	'frame_enhancer_blend' : int,
	'lip_syncer_model' : LipSyncerModel
})
FrameProcessorStateSet = Dict[StateContext, FrameProcessorState]
