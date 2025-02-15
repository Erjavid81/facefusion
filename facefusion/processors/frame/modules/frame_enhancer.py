from argparse import ArgumentParser
from time import sleep
from typing import Any, List, Literal, Optional

import cv2
import numpy

import facefusion.jobs.job_manager
import facefusion.jobs.job_store
import facefusion.processors.frame.core as frame_processors
from facefusion import config, logger, process_manager, state_manager, wording
from facefusion.common_helper import create_metavar
from facefusion.content_analyser import clear_content_analyser
from facefusion.download import conditional_download, is_download_done
from facefusion.execution import create_inference_session
from facefusion.face_analyser import clear_face_analyser
from facefusion.filesystem import in_directory, is_file, is_image, is_video, resolve_relative_path, same_file_extension
from facefusion.processors.frame import choices as frame_processors_choices
from facefusion.processors.frame.typing import FrameEnhancerInputs
from facefusion.program_helper import find_argument_group
from facefusion.thread_helper import conditional_thread_semaphore, thread_lock
from facefusion.typing import Args, Face, ModelSet, OptionsWithModel, ProcessMode, QueuePayload, UpdateProgress, VisionFrame
from facefusion.vision import create_tile_frames, merge_tile_frames, read_image, read_static_image, write_image

FRAME_PROCESSOR = None
NAME = __name__.upper()
MODELS : ModelSet =\
{
	'clear_reality_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/clear_reality_x4.onnx',
		'path': resolve_relative_path('../.assets/models/clear_reality_x4.onnx'),
		'size': (128, 8, 4),
		'scale': 4
	},
	'lsdir_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/lsdir_x4.onnx',
		'path': resolve_relative_path('../.assets/models/lsdir_x4.onnx'),
		'size': (128, 8, 4),
		'scale': 4
	},
	'nomos8k_sc_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/nomos8k_sc_x4.onnx',
		'path': resolve_relative_path('../.assets/models/nomos8k_sc_x4.onnx'),
		'size': (128, 8, 4),
		'scale': 4
	},
	'real_esrgan_x2':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x2.onnx',
		'path': resolve_relative_path('../.assets/models/real_esrgan_x2.onnx'),
		'size': (256, 16, 8),
		'scale': 2
	},
	'real_esrgan_x2_fp16':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x2_fp16.onnx',
		'path': resolve_relative_path('../.assets/models/real_esrgan_x2_fp16.onnx'),
		'size': (256, 16, 8),
		'scale': 2
	},
	'real_esrgan_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x4.onnx',
		'path': resolve_relative_path('../.assets/models/real_esrgan_x4.onnx'),
		'size': (256, 16, 8),
		'scale': 4
	},
	'real_esrgan_x4_fp16':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x4_fp16.onnx',
		'path': resolve_relative_path('../.assets/models/real_esrgan_x4_fp16.onnx'),
		'size': (256, 16, 8),
		'scale': 4
	},
	'real_esrgan_x8':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x8.onnx',
		'path': resolve_relative_path('../.assets/models/real_esrgan_x8.onnx'),
		'size': (256, 16, 8),
		'scale': 8
	},
	'real_esrgan_x8_fp16':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_esrgan_x8_fp16.onnx',
		'path': resolve_relative_path('../.assets/models/real_esrgan_x8_fp16.onnx'),
		'size': (256, 16, 8),
		'scale': 8
	},
	'real_hatgan_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/real_hatgan_x4.onnx',
		'path': resolve_relative_path('../.assets/models/real_hatgan_x4.onnx'),
		'size': (256, 16, 8),
		'scale': 4
	},
	'span_kendata_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/span_kendata_x4.onnx',
		'path': resolve_relative_path('../.assets/models/span_kendata_x4.onnx'),
		'size': (128, 8, 4),
		'scale': 4
	},
	'ultra_sharp_x4':
	{
		'url': 'https://github.com/facefusion/facefusion-assets/releases/download/models/ultra_sharp_x4.onnx',
		'path': resolve_relative_path('../.assets/models/ultra_sharp_x4.onnx'),
		'size': (128, 8, 4),
		'scale': 4
	}
}
OPTIONS : Optional[OptionsWithModel] = None


def get_frame_processor() -> Any:
	global FRAME_PROCESSOR

	with thread_lock():
		while process_manager.is_checking():
			sleep(0.5)
		if FRAME_PROCESSOR is None:
			model_path = get_options('model').get('path')
			FRAME_PROCESSOR = create_inference_session(model_path, state_manager.get_item('execution_device_id'), state_manager.get_item('execution_providers'))
	return FRAME_PROCESSOR


def clear_frame_processor() -> None:
	global FRAME_PROCESSOR

	FRAME_PROCESSOR = None


def get_options(key : Literal['model']) -> Any:
	global OPTIONS

	if OPTIONS is None:
		OPTIONS =\
		{
			'model': MODELS[state_manager.get_item('frame_enhancer_model')]
		}
	return OPTIONS.get(key)


def set_options(key : Literal['model'], value : Any) -> None:
	global OPTIONS

	OPTIONS[key] = value


def register_args(program : ArgumentParser) -> None:
	group_frame_processors = find_argument_group(program, 'frame processors')
	if group_frame_processors:
		group_frame_processors.add_argument('--frame-enhancer-model', help = wording.get('help.frame_enhancer_model'), default = config.get_str_value('frame_processors.frame_enhancer_model', 'span_kendata_x4'), choices = frame_processors_choices.frame_enhancer_models)
		group_frame_processors.add_argument('--frame-enhancer-blend', help = wording.get('help.frame_enhancer_blend'), type = int, default = config.get_int_value('frame_processors.frame_enhancer_blend', '80'), choices = frame_processors_choices.frame_enhancer_blend_range, metavar = create_metavar(frame_processors_choices.frame_enhancer_blend_range))
		facefusion.jobs.job_store.register_step_keys([ 'frame_enhancer_model', 'frame_enhancer_blend' ])


def apply_args(args : Args) -> None:
	state_manager.init_item('frame_enhancer_model', args.get('frame_enhancer_model'))
	state_manager.init_item('frame_enhancer_blend', args.get('frame_enhancer_blend'))


def pre_check() -> bool:
	download_directory_path = resolve_relative_path('../.assets/models')
	model_url = get_options('model').get('url')
	model_path = get_options('model').get('path')

	if not state_manager.get_item('skip_download'):
		process_manager.check()
		conditional_download(download_directory_path, [ model_url ])
		process_manager.end()
	return is_file(model_path)


def post_check() -> bool:
	model_url = get_options('model').get('url')
	model_path = get_options('model').get('path')

	if not state_manager.get_item('skip_download') and not is_download_done(model_url, model_path):
		logger.error(wording.get('model_download_not_done') + wording.get('exclamation_mark'), NAME)
		return False
	if not is_file(model_path):
		logger.error(wording.get('model_file_not_present') + wording.get('exclamation_mark'), NAME)
		return False
	return True


def pre_process(mode : ProcessMode) -> bool:
	if mode in [ 'output', 'preview' ] and not is_image(state_manager.get_item('target_path')) and not is_video(state_manager.get_item('target_path')):
		logger.error(wording.get('choose_image_or_video_target') + wording.get('exclamation_mark'), NAME)
		return False
	if mode == 'output' and not in_directory(state_manager.get_item('output_path')):
		logger.error(wording.get('specify_image_or_video_output') + wording.get('exclamation_mark'), NAME)
		return False
	if mode == 'output' and not same_file_extension([ state_manager.get_item('target_path'), state_manager.get_item('output_path') ]):
		logger.error(wording.get('match_target_and_output_extension') + wording.get('exclamation_mark'), NAME)
		return False
	return True


def post_process() -> None:
	read_static_image.cache_clear()
	if state_manager.get_item('video_memory_strategy') in [ 'strict', 'moderate' ]:
		clear_frame_processor()
	if state_manager.get_item('video_memory_strategy') == 'strict':
		clear_face_analyser()
		clear_content_analyser()


def enhance_frame(temp_vision_frame : VisionFrame) -> VisionFrame:
	frame_processor = get_frame_processor()
	size = get_options('model').get('size')
	scale = get_options('model').get('scale')
	temp_height, temp_width = temp_vision_frame.shape[:2]
	tile_vision_frames, pad_width, pad_height = create_tile_frames(temp_vision_frame, size)

	for index, tile_vision_frame in enumerate(tile_vision_frames):
		with conditional_thread_semaphore():
			tile_vision_frame = frame_processor.run(None,
			{
				frame_processor.get_inputs()[0].name : prepare_tile_frame(tile_vision_frame)
			})[0]
		tile_vision_frames[index] = normalize_tile_frame(tile_vision_frame)

	merge_vision_frame = merge_tile_frames(tile_vision_frames, temp_width * scale, temp_height * scale, pad_width * scale, pad_height * scale, (size[0] * scale, size[1] * scale, size[2] * scale))
	temp_vision_frame = blend_frame(temp_vision_frame, merge_vision_frame)
	return temp_vision_frame


def prepare_tile_frame(vision_tile_frame : VisionFrame) -> VisionFrame:
	vision_tile_frame = numpy.expand_dims(vision_tile_frame[:, :, ::-1], axis = 0)
	vision_tile_frame = vision_tile_frame.transpose(0, 3, 1, 2)
	vision_tile_frame = vision_tile_frame.astype(numpy.float32) / 255
	return vision_tile_frame


def normalize_tile_frame(vision_tile_frame : VisionFrame) -> VisionFrame:
	vision_tile_frame = vision_tile_frame.transpose(0, 2, 3, 1).squeeze(0) * 255
	vision_tile_frame = vision_tile_frame.clip(0, 255).astype(numpy.uint8)[:, :, ::-1]
	return vision_tile_frame


def blend_frame(temp_vision_frame : VisionFrame, merge_vision_frame : VisionFrame) -> VisionFrame:
	frame_enhancer_blend = 1 - (state_manager.get_item('frame_enhancer_blend') / 100)
	temp_vision_frame = cv2.resize(temp_vision_frame, (merge_vision_frame.shape[1], merge_vision_frame.shape[0]))
	temp_vision_frame = cv2.addWeighted(temp_vision_frame, frame_enhancer_blend, merge_vision_frame, 1 - frame_enhancer_blend, 0)
	return temp_vision_frame


def get_reference_frame(source_face : Face, target_face : Face, temp_vision_frame : VisionFrame) -> VisionFrame:
	pass


def process_frame(inputs : FrameEnhancerInputs) -> VisionFrame:
	target_vision_frame = inputs.get('target_vision_frame')
	return enhance_frame(target_vision_frame)


def process_frames(source_paths : List[str], queue_payloads : List[QueuePayload], update_progress : UpdateProgress) -> None:
	for queue_payload in process_manager.manage(queue_payloads):
		target_vision_path = queue_payload['frame_path']
		target_vision_frame = read_image(target_vision_path)
		output_vision_frame = process_frame(
		{
			'target_vision_frame': target_vision_frame
		})
		write_image(target_vision_path, output_vision_frame)
		update_progress(1)


def process_image(source_paths : List[str], target_path : str, output_path : str) -> None:
	target_vision_frame = read_static_image(target_path)
	output_vision_frame = process_frame(
	{
		'target_vision_frame': target_vision_frame
	})
	write_image(output_path, output_vision_frame)


def process_video(source_paths : List[str], temp_frame_paths : List[str]) -> None:
	frame_processors.multi_process_frames(None, temp_frame_paths, process_frames)
