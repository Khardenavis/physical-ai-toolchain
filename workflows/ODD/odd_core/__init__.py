# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""ODD Scene Variation & Coverage Analysis Package."""

from .annotator import VLMAnnotator, clean_reasoning_tags, extract_first_frame_b64
from .engine import (
    BASE_VIDEO_FILTERS,
    QA_SPEC_ATTRIBUTE_ALIASES,
    AttributeReport,
    AttributeSpec,
    CategorySpec,
    ODDCoverageConfig,
    ODDCoverageEngine,
    SceneRecord,
    build_category_summary,
    calculate_needed_variations,
    filter_spec_by_qa_template,
    format_category_summary,
    generate_variations_for_gaps,
    load_scenes_from_annotations,
    modify_annotation_for_attribute,
    normalize_attribute_string,
    select_base_videos_for_attribute,
)

__all__ = [
    "ODDCoverageConfig",
    "ODDCoverageEngine",
    "SceneRecord",
    "AttributeSpec",
    "CategorySpec",
    "AttributeReport",
    "load_scenes_from_annotations",
    "generate_variations_for_gaps",
    "build_category_summary",
    "format_category_summary",
    "select_base_videos_for_attribute",
    "calculate_needed_variations",
    "filter_spec_by_qa_template",
    "modify_annotation_for_attribute",
    "normalize_attribute_string",
    "BASE_VIDEO_FILTERS",
    "QA_SPEC_ATTRIBUTE_ALIASES",
    "VLMAnnotator",
    "clean_reasoning_tags",
    "extract_first_frame_b64",
]
