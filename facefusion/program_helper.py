from argparse import ArgumentParser, _ArgumentGroup
from typing import List, Optional

import facefusion.choices
from facefusion.processors.frame import choices as frame_processors_choices


def find_argument_group(program : ArgumentParser, group_name : str) -> Optional[_ArgumentGroup]:
	for group in program._action_groups:
		if group.title == group_name:
			return group
	return None


def validate_args(program : ArgumentParser) -> bool:
	for action in program._actions:
		if action.default and action.choices:
			if isinstance(action.default, list):
				if any(default not in action.choices for default in action.default):
					return False
			elif action.default not in action.choices:
				return False
	return True


def suggest_face_detector_choices(program : ArgumentParser) -> List[str]:
	known_args, _ = program.parse_known_args()
	return facefusion.choices.face_detector_set.get(known_args.face_detector_model) #type:ignore[call-overload]


def suggest_face_swapper_pixel_boost_choices(program : ArgumentParser) -> List[str]:
	known_args, _ = program.parse_known_args()
	return frame_processors_choices.face_swapper_set.get(known_args.face_swapper_model) #type:ignore[call-overload]
