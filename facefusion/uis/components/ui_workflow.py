from typing import Optional, Tuple

import gradio

import facefusion
from facefusion import state_manager, wording
from facefusion.typing import UiWorkflow
from facefusion.uis.core import get_ui_component

UI_WORKFLOW_DROPDOWN : Optional[gradio.Dropdown] = None


def render() -> None:
	global UI_WORKFLOW_DROPDOWN

	UI_WORKFLOW_DROPDOWN = gradio.Dropdown(
		label = wording.get('uis.ui_workflow'),
		choices = facefusion.choices.ui_workflows,
		value = state_manager.get_item('ui_workflow')
	)


def listen() -> None:
	instant_runner_wrapper = get_ui_component('instant_runner_wrapper')
	job_runner_wrapper = get_ui_component('job_runner_wrapper')
	job_manager_wrapper = get_ui_component('job_manager_wrapper')

	if instant_runner_wrapper and job_runner_wrapper and job_manager_wrapper:
		UI_WORKFLOW_DROPDOWN.change(update_ui_workflow, inputs = UI_WORKFLOW_DROPDOWN, outputs = [ instant_runner_wrapper, job_runner_wrapper, job_manager_wrapper ])


def update_ui_workflow(ui_workflow : UiWorkflow) -> Tuple[gradio.Group, gradio.Group, gradio.Group]:
	return gradio.Group(visible = ui_workflow == 'instant_runner'), gradio.Group(visible = ui_workflow == 'job_runner'), gradio.Group(visible = ui_workflow == 'job_manager')
