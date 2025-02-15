from typing import List, Optional, Tuple

import gradio

import facefusion.choices
from facefusion import state_manager, wording
from facefusion.typing import FaceMaskRegion, FaceMaskType
from facefusion.uis.core import register_ui_component

FACE_MASK_TYPES_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None
FACE_MASK_WRAPPER : Optional[gradio.Group] = None
FACE_MASK_BLUR_SLIDER : Optional[gradio.Slider] = None
FACE_MASK_PADDING_TOP_SLIDER : Optional[gradio.Slider] = None
FACE_MASK_PADDING_RIGHT_SLIDER : Optional[gradio.Slider] = None
FACE_MASK_PADDING_BOTTOM_SLIDER : Optional[gradio.Slider] = None
FACE_MASK_PADDING_LEFT_SLIDER : Optional[gradio.Slider] = None
FACE_MASK_REGION_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None


def render() -> None:
	global FACE_MASK_TYPES_CHECKBOX_GROUP
	global FACE_MASK_WRAPPER
	global FACE_MASK_BLUR_SLIDER
	global FACE_MASK_PADDING_TOP_SLIDER
	global FACE_MASK_PADDING_RIGHT_SLIDER
	global FACE_MASK_PADDING_BOTTOM_SLIDER
	global FACE_MASK_PADDING_LEFT_SLIDER
	global FACE_MASK_REGION_CHECKBOX_GROUP

	has_box_mask = 'box' in state_manager.get_item('face_mask_types')
	has_region_mask = 'region' in state_manager.get_item('face_mask_types')
	FACE_MASK_TYPES_CHECKBOX_GROUP = gradio.CheckboxGroup(
		label = wording.get('uis.face_mask_types_checkbox_group'),
		choices = facefusion.choices.face_mask_types,
		value = state_manager.get_item('face_mask_types')
	)
	with gradio.Column(visible = has_box_mask) as FACE_MASK_WRAPPER:
		FACE_MASK_BLUR_SLIDER = gradio.Slider(
			label = wording.get('uis.face_mask_blur_slider'),
			step = facefusion.choices.face_mask_blur_range[1] - facefusion.choices.face_mask_blur_range[0],
			minimum = facefusion.choices.face_mask_blur_range[0],
			maximum = facefusion.choices.face_mask_blur_range[-1],
			value = state_manager.get_item('face_mask_blur')
		)
		with gradio.Group():
			with gradio.Row():
				FACE_MASK_PADDING_TOP_SLIDER = gradio.Slider(
					label = wording.get('uis.face_mask_padding_top_slider'),
					step = facefusion.choices.face_mask_padding_range[1] - facefusion.choices.face_mask_padding_range[0],
					minimum = facefusion.choices.face_mask_padding_range[0],
					maximum = facefusion.choices.face_mask_padding_range[-1],
					value = state_manager.get_item('face_mask_padding')[0]
				)
				FACE_MASK_PADDING_RIGHT_SLIDER = gradio.Slider(
					label = wording.get('uis.face_mask_padding_right_slider'),
					step = facefusion.choices.face_mask_padding_range[1] - facefusion.choices.face_mask_padding_range[0],
					minimum = facefusion.choices.face_mask_padding_range[0],
					maximum = facefusion.choices.face_mask_padding_range[-1],
					value = state_manager.get_item('face_mask_padding')[1]
				)
			with gradio.Row():
				FACE_MASK_PADDING_BOTTOM_SLIDER = gradio.Slider(
					label = wording.get('uis.face_mask_padding_bottom_slider'),
					step = facefusion.choices.face_mask_padding_range[1] - facefusion.choices.face_mask_padding_range[0],
					minimum = facefusion.choices.face_mask_padding_range[0],
					maximum = facefusion.choices.face_mask_padding_range[-1],
					value = state_manager.get_item('face_mask_padding')[2]
				)
				FACE_MASK_PADDING_LEFT_SLIDER = gradio.Slider(
					label = wording.get('uis.face_mask_padding_left_slider'),
					step = facefusion.choices.face_mask_padding_range[1] - facefusion.choices.face_mask_padding_range[0],
					minimum = facefusion.choices.face_mask_padding_range[0],
					maximum = facefusion.choices.face_mask_padding_range[-1],
					value = state_manager.get_item('face_mask_padding')[3]
				)
		FACE_MASK_REGION_CHECKBOX_GROUP = gradio.CheckboxGroup(
			label = wording.get('uis.face_mask_region_checkbox_group'),
			choices = facefusion.choices.face_mask_regions,
			value = state_manager.get_item('face_mask_regions'),
			visible = has_region_mask
		)
	register_ui_component('face_mask_types_checkbox_group', FACE_MASK_TYPES_CHECKBOX_GROUP)
	register_ui_component('face_mask_blur_slider', FACE_MASK_BLUR_SLIDER)
	register_ui_component('face_mask_padding_top_slider', FACE_MASK_PADDING_TOP_SLIDER)
	register_ui_component('face_mask_padding_right_slider', FACE_MASK_PADDING_RIGHT_SLIDER)
	register_ui_component('face_mask_padding_bottom_slider', FACE_MASK_PADDING_BOTTOM_SLIDER)
	register_ui_component('face_mask_padding_left_slider', FACE_MASK_PADDING_LEFT_SLIDER)
	register_ui_component('face_mask_region_checkbox_group', FACE_MASK_REGION_CHECKBOX_GROUP)


def listen() -> None:
	FACE_MASK_TYPES_CHECKBOX_GROUP.change(update_face_mask_type, inputs = FACE_MASK_TYPES_CHECKBOX_GROUP, outputs = [FACE_MASK_TYPES_CHECKBOX_GROUP, FACE_MASK_WRAPPER, FACE_MASK_REGION_CHECKBOX_GROUP])
	FACE_MASK_BLUR_SLIDER.release(update_face_mask_blur, inputs = FACE_MASK_BLUR_SLIDER)
	FACE_MASK_REGION_CHECKBOX_GROUP.change(update_face_mask_regions, inputs = FACE_MASK_REGION_CHECKBOX_GROUP, outputs = FACE_MASK_REGION_CHECKBOX_GROUP)
	face_mask_padding_sliders = [ FACE_MASK_PADDING_TOP_SLIDER, FACE_MASK_PADDING_RIGHT_SLIDER, FACE_MASK_PADDING_BOTTOM_SLIDER, FACE_MASK_PADDING_LEFT_SLIDER ]
	for face_mask_padding_slider in face_mask_padding_sliders:
		face_mask_padding_slider.release(update_face_mask_padding, inputs = face_mask_padding_sliders)


def update_face_mask_type(face_mask_types : List[FaceMaskType]) -> Tuple[gradio.CheckboxGroup, gradio.Group, gradio.CheckboxGroup]:
	face_mask_types = face_mask_types or facefusion.choices.face_mask_types
	state_manager.set_item('face_mask_types', face_mask_types)
	has_box_mask = 'box' in face_mask_types
	has_region_mask = 'region' in face_mask_types
	return gradio.CheckboxGroup(value = state_manager.get_item('face_mask_types')), gradio.Group(visible = has_box_mask), gradio.CheckboxGroup(visible = has_region_mask)


def update_face_mask_blur(face_mask_blur : float) -> None:
	state_manager.set_item('face_mask_blur', face_mask_blur)


def update_face_mask_padding(face_mask_padding_top : float, face_mask_padding_right : float, face_mask_padding_bottom : float, face_mask_padding_left : float) -> None:
	face_mask_padding = (int(face_mask_padding_top), int(face_mask_padding_right), int(face_mask_padding_bottom), int(face_mask_padding_left))
	state_manager.set_item('face_mask_padding', face_mask_padding)


def update_face_mask_regions(face_mask_regions : List[FaceMaskRegion]) -> gradio.CheckboxGroup:
	face_mask_regions = face_mask_regions or facefusion.choices.face_mask_regions
	state_manager.set_item('face_mask_regions', face_mask_regions)
	return gradio.CheckboxGroup(value = state_manager.get_item('face_mask_regions'))
