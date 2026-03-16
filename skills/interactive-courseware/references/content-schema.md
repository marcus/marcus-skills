# Content Data Schema Reference

Formal schema definition for course content JSON files. This is the contract between content-generating agents and the course player runtime. Agents produce `content.json` files conforming to this schema; the `ContentRenderer` component consumes them.

---

## JSON Schema Definition

The schema uses JSON Schema Draft 2020-12. It defines a single module file — each module in `content/modules/<id>/content.json` must validate against this schema.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://courseware.internal/schemas/module-content.schema.json",
  "title": "Course Module Content",
  "description": "Schema for a single course module content.json file. Defines module metadata, content blocks, and assessment items.",
  "type": "object",
  "required": ["module", "title", "objectives", "blocks"],
  "additionalProperties": false,
  "properties": {
    "module": {
      "type": "string",
      "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$",
      "description": "Module identifier matching the directory name. Kebab-case, e.g. '01-introduction'."
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 120,
      "description": "Human-readable module title displayed in navigation and headers."
    },
    "objectives": {
      "type": "array",
      "minItems": 1,
      "maxItems": 7,
      "items": {
        "type": "string",
        "minLength": 10,
        "description": "A behavioral learning objective. Must describe what the learner will be able to DO, not what they will 'understand' or 'know'."
      },
      "description": "Learning objectives for this module. Each must be measurable and action-oriented."
    },
    "duration_minutes": {
      "type": "integer",
      "minimum": 1,
      "maximum": 120,
      "description": "Estimated completion time in minutes. Used for progress estimation and LMS reporting."
    },
    "prerequisite_modules": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"
      },
      "description": "Module IDs that must be completed before this module unlocks. Empty array or omitted means no prerequisites."
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Freeform tags for search, filtering, and analytics. E.g. ['compliance', 'phishing', 'beginner']."
    },
    "blocks": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/block" },
      "description": "Ordered sequence of content blocks that make up this module."
    }
  },

  "$defs": {

    "block": {
      "discriminator": { "propertyName": "type" },
      "oneOf": [
        { "$ref": "#/$defs/narrative_block" },
        { "$ref": "#/$defs/branch_block" },
        { "$ref": "#/$defs/knowledge_check_block" },
        { "$ref": "#/$defs/drag_drop_block" },
        { "$ref": "#/$defs/hotspot_block" },
        { "$ref": "#/$defs/scroll_story_block" },
        { "$ref": "#/$defs/interactive_video_block" },
        { "$ref": "#/$defs/simulation_block" },
        { "$ref": "#/$defs/dialogue_block" },
        { "$ref": "#/$defs/code_playground_block" }
      ]
    },

    "media_ref": {
      "type": "object",
      "description": "Reference to a media asset. Paths are relative to the module's media/ directory.",
      "properties": {
        "src": {
          "type": "string",
          "description": "Path to the media file relative to the module directory, e.g. 'media/intro-narration.mp3'."
        },
        "alt": {
          "type": "string",
          "description": "Alt text for images. Required for images, ignored for audio/video."
        },
        "mime_type": {
          "type": "string",
          "pattern": "^(audio|video|image)/[a-z0-9.+-]+$",
          "description": "MIME type. Inferred from extension if omitted."
        },
        "duration_seconds": {
          "type": "number",
          "minimum": 0,
          "description": "Duration in seconds for audio/video assets. Populated by the media pipeline."
        },
        "caption_src": {
          "type": "string",
          "description": "Path to a WebVTT (.vtt) caption file for audio/video. Required for accessibility."
        }
      },
      "required": ["src"]
    },

    "voice_role": {
      "type": "string",
      "enum": ["narrator", "learner", "mentor", "system", "character-1", "character-2", "character-3", "character-4", "character-5"],
      "description": "Voice role for TTS generation. Maps to voice IDs in shared/voice-config.json. Use 'narrator' for exposition, 'learner' for the learner's inner voice, 'mentor' for guidance, 'system' for UI feedback, and 'character-N' for scenario characters."
    },

    "feedback_object": {
      "type": "object",
      "description": "Feedback text keyed by outcome.",
      "properties": {
        "correct": { "type": "string", "description": "Shown when the learner answers correctly." },
        "incorrect": { "type": "string", "description": "Shown when the learner answers incorrectly." },
        "partial": { "type": "string", "description": "Shown when the learner's answer is partially correct." }
      },
      "required": ["correct", "incorrect"]
    },

    "scoring": {
      "type": "object",
      "description": "Scoring configuration for assessed blocks.",
      "properties": {
        "points": {
          "type": "integer",
          "minimum": 0,
          "description": "Maximum points available for this block."
        },
        "passing_fraction": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Fraction of points required to pass. 0.7 means 70%."
        },
        "attempts_allowed": {
          "type": "integer",
          "minimum": 1,
          "description": "Number of attempts permitted. Omit for unlimited."
        },
        "penalty_per_retry": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Fraction of points deducted per retry. 0.25 means 25% penalty per additional attempt."
        },
        "objective_ids": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Learning objective IDs this assessment maps to. Used for objective mastery tracking."
        }
      }
    },

    "base_block_properties": {
      "type": "object",
      "description": "Properties shared by all block types.",
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$",
          "description": "Unique block identifier within this module. Used for navigation targets and analytics."
        },
        "narration": {
          "$ref": "#/$defs/media_ref",
          "description": "Audio narration for this block."
        },
        "narration_text": {
          "type": "string",
          "description": "Text for TTS generation. The media pipeline reads this, generates audio, and populates the 'narration' field."
        },
        "voice_role": {
          "$ref": "#/$defs/voice_role",
          "description": "Which voice to use for narrating this block."
        },
        "background_audio": {
          "type": "string",
          "description": "Background audio track ID from shared/audio-tracks.json, e.g. 'ambient-office', 'tension-building'."
        },
        "image": {
          "$ref": "#/$defs/media_ref",
          "description": "Primary image for this block. Populated by the Media Agent after generation."
        },
        "illustration_prompt": {
          "type": "string",
          "description": "Generation-time field: text prompt for the Media Agent to generate an illustration. The Media Agent replaces this with a populated 'image' media_ref after generation. Not consumed by the course player."
        },
        "transition": {
          "type": "string",
          "enum": ["fade", "slide-left", "slide-right", "slide-up", "zoom", "none"],
          "default": "fade",
          "description": "Entrance transition animation for this block."
        },
        "requires_completion": {
          "type": "boolean",
          "default": false,
          "description": "If true, the learner cannot advance past this block without completing its interaction."
        }
      }
    },

    "narrative_block": {
      "type": "object",
      "description": "Narrative content — expository text, scene-setting, or storytelling. The most common block type.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "text"],
      "properties": {
        "type": { "const": "narrative" },
        "id": true,
        "text": {
          "type": "string",
          "description": "The narrative content. Supports Markdown for basic formatting (bold, italic, lists, links)."
        },
        "heading": {
          "type": "string",
          "description": "Optional heading displayed above the narrative text."
        },
        "callout": {
          "type": "object",
          "properties": {
            "type": { "type": "string", "enum": ["tip", "warning", "info", "example"] },
            "text": { "type": "string" }
          },
          "required": ["type", "text"],
          "description": "Optional callout box displayed alongside the narrative."
        },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "branch_block": {
      "type": "object",
      "description": "Branching decision point. Learner chooses from options, each with consequences and routing.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "prompt", "choices"],
      "properties": {
        "type": { "const": "branch" },
        "id": true,
        "prompt": {
          "type": "string",
          "description": "The scenario prompt or question the learner must respond to."
        },
        "context": {
          "type": "string",
          "description": "Optional scene-setting text displayed before the prompt."
        },
        "choices": {
          "type": "array",
          "minItems": 2,
          "maxItems": 6,
          "items": {
            "type": "object",
            "required": ["text", "consequence", "feedback"],
            "properties": {
              "text": { "type": "string", "description": "The choice label shown to the learner." },
              "consequence": {
                "type": "string",
                "enum": ["good", "partial", "bad", "neutral"],
                "description": "Outcome quality. Drives scoring and visual treatment."
              },
              "feedback": { "type": "string", "description": "Explanation shown after this choice is selected." },
              "next": {
                "type": "string",
                "description": "Block ID to navigate to after this choice. If omitted, continues to the next sequential block."
              },
              "points": {
                "type": "integer",
                "minimum": 0,
                "description": "Points awarded for selecting this choice."
              }
            }
          }
        },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "knowledge_check_block": {
      "type": "object",
      "description": "Assessment question with elaborative feedback. Supports multiple question formats.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "question", "format"],
      "properties": {
        "type": { "const": "knowledge-check" },
        "id": true,
        "question": {
          "type": "string",
          "description": "The question stem."
        },
        "format": {
          "type": "string",
          "enum": ["single-choice", "multi-choice", "drag-drop-sort", "hotspot", "confidence-rated", "free-response"],
          "description": "Question presentation format."
        },
        "options": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "object",
            "required": ["text"],
            "properties": {
              "text": { "type": "string", "description": "Option label." },
              "correct": { "type": "boolean", "default": false, "description": "Whether this is the correct answer." },
              "partial": { "type": "boolean", "default": false, "description": "Whether this is a partially correct answer. Scores between correct and incorrect." }
            }
          },
          "description": "Answer options. Required for single-choice, multi-choice, and confidence-rated formats."
        },
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["text", "correct_position"],
            "properties": {
              "text": { "type": "string", "description": "Item label." },
              "correct_position": { "type": "integer", "minimum": 1, "description": "The correct ordinal position (1-based)." }
            }
          },
          "description": "Sortable items. Required for drag-drop-sort format."
        },
        "hotspot_image": {
          "$ref": "#/$defs/media_ref",
          "description": "Image containing hotspot targets. Required for hotspot format."
        },
        "hotspots": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["x", "y", "width", "height", "label"],
            "properties": {
              "x": { "type": "number", "description": "X coordinate of the hotspot region (pixels from left)." },
              "y": { "type": "number", "description": "Y coordinate of the hotspot region (pixels from top)." },
              "width": { "type": "number", "description": "Width of the hotspot region in pixels." },
              "height": { "type": "number", "description": "Height of the hotspot region in pixels." },
              "label": { "type": "string", "description": "Accessible label describing what this hotspot represents." }
            }
          },
          "description": "Clickable target regions on the hotspot image. Required for hotspot format."
        },
        "required_correct": {
          "type": "integer",
          "minimum": 1,
          "description": "Number of hotspots the learner must correctly identify. Required for hotspot format."
        },
        "confidence_prompt": {
          "type": "string",
          "description": "Prompt asking the learner to rate their confidence. Required for confidence-rated format."
        },
        "confidence_levels": {
          "type": "array",
          "minItems": 2,
          "items": { "type": "string" },
          "description": "Confidence level labels, low to high. Required for confidence-rated format. E.g. ['Guessing', 'Somewhat confident', 'Very confident']."
        },
        "rubric": {
          "type": "string",
          "description": "Grading rubric or criteria description. Required for free-response format."
        },
        "sample_answer": {
          "type": "string",
          "description": "Model answer for free-response questions. Shown after the learner submits."
        },
        "feedback": {
          "oneOf": [
            { "$ref": "#/$defs/feedback_object" },
            {
              "type": "object",
              "description": "Extended feedback for confidence-rated questions.",
              "properties": {
                "correct_high_confidence": { "type": "string" },
                "correct_low_confidence": { "type": "string" },
                "incorrect_high_confidence": { "type": "string" },
                "incorrect_low_confidence": { "type": "string" }
              },
              "required": ["correct_high_confidence", "correct_low_confidence", "incorrect_high_confidence", "incorrect_low_confidence"]
            }
          ],
          "description": "Feedback text keyed by outcome. Structure depends on the question format."
        },
        "difficulty": {
          "type": "string",
          "enum": ["beginner", "intermediate", "advanced"],
          "description": "Difficulty tier for adaptive sequencing."
        },
        "bloom_level": {
          "type": "string",
          "enum": ["remember", "understand", "apply", "analyze", "evaluate", "create"],
          "description": "Bloom's taxonomy level this question targets."
        },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "drag_drop_block": {
      "type": "object",
      "description": "Standalone drag-and-drop interaction — categorization, labeling, or assembly. For sequencing/sorting, use knowledge-check with format 'drag-drop-sort' instead.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "variant", "instruction", "items", "targets"],
      "properties": {
        "type": { "const": "drag-drop" },
        "id": true,
        "variant": {
          "type": "string",
          "enum": ["categorize", "label", "assemble", "match"],
          "description": "The drag-drop interaction style."
        },
        "instruction": {
          "type": "string",
          "description": "Instructions explaining what the learner should do."
        },
        "items": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "object",
            "required": ["id", "content", "target_id"],
            "properties": {
              "id": { "type": "string", "description": "Unique item identifier." },
              "content": { "type": "string", "description": "Text or image reference for the draggable item." },
              "content_type": {
                "type": "string",
                "enum": ["text", "image"],
                "default": "text"
              },
              "target_id": { "type": "string", "description": "ID of the correct drop target." }
            }
          },
          "description": "Draggable items the learner places onto targets."
        },
        "targets": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["id", "label"],
            "properties": {
              "id": { "type": "string", "description": "Unique target identifier." },
              "label": { "type": "string", "description": "Target label displayed to the learner." },
              "x": { "type": "number", "description": "X position for label-on-image variant." },
              "y": { "type": "number", "description": "Y position for label-on-image variant." }
            }
          },
          "description": "Drop target zones."
        },
        "background_image": {
          "$ref": "#/$defs/media_ref",
          "description": "Background image for label and assemble variants."
        },
        "feedback": { "$ref": "#/$defs/feedback_object" },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "hotspot_block": {
      "type": "object",
      "description": "Standalone hotspot exploration — learner clicks regions on an image to reveal information. For assessed hotspot identification, use knowledge-check with format 'hotspot' instead.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "instruction", "hotspot_image", "regions"],
      "properties": {
        "type": { "const": "hotspot" },
        "id": true,
        "instruction": {
          "type": "string",
          "description": "Prompt telling the learner what to explore."
        },
        "hotspot_image": {
          "$ref": "#/$defs/media_ref",
          "description": "The image containing clickable regions."
        },
        "regions": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["id", "x", "y", "width", "height", "label", "content"],
            "properties": {
              "id": { "type": "string" },
              "x": { "type": "number" },
              "y": { "type": "number" },
              "width": { "type": "number" },
              "height": { "type": "number" },
              "shape": {
                "type": "string",
                "enum": ["rect", "circle", "polygon"],
                "default": "rect"
              },
              "label": { "type": "string", "description": "Accessible label for the region." },
              "content": { "type": "string", "description": "Information revealed when this region is activated." },
              "narration_text": { "type": "string", "description": "TTS text spoken when this region is activated." },
              "voice_role": { "$ref": "#/$defs/voice_role" }
            }
          },
          "description": "Clickable regions that reveal content."
        },
        "require_all": {
          "type": "boolean",
          "default": false,
          "description": "If true, learner must click all regions before advancing."
        },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "scroll_story_block": {
      "type": "object",
      "description": "Scroll-driven storytelling section using GSAP ScrollTrigger. Content reveals tied to scroll position.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "sections"],
      "properties": {
        "type": { "const": "scroll-story" },
        "id": true,
        "sections": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "object",
            "required": ["id", "content"],
            "properties": {
              "id": { "type": "string" },
              "title": { "type": "string", "description": "Section heading." },
              "content": { "type": "string", "description": "Section body text. Supports Markdown." },
              "visual": {
                "$ref": "#/$defs/media_ref",
                "description": "Image or video displayed alongside this section."
              },
              "animation": {
                "type": "string",
                "enum": ["fade-up", "slide-left", "slide-right", "scale-in", "parallax", "none"],
                "default": "fade-up",
                "description": "Scroll-triggered entrance animation."
              },
              "pin": {
                "type": "boolean",
                "default": false,
                "description": "If true, this section pins in place while the learner scrolls through its content."
              },
              "narration_text": { "type": "string" },
              "voice_role": { "$ref": "#/$defs/voice_role" }
            }
          },
          "description": "Ordered sections that compose the scroll-driven narrative."
        },
        "show_progress_bar": {
          "type": "boolean",
          "default": true,
          "description": "Whether to display a horizontal scroll progress indicator."
        },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "interactive_video_block": {
      "type": "object",
      "description": "Video with time-synced events — quizzes, panel updates, hotspots, and chapter markers overlaid on playback.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "video"],
      "properties": {
        "type": { "const": "interactive-video" },
        "id": true,
        "video": {
          "$ref": "#/$defs/media_ref",
          "description": "The video file. Must include caption_src for accessibility."
        },
        "events": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["time", "event_type"],
            "properties": {
              "time": { "type": "number", "minimum": 0, "description": "Trigger time in seconds from video start." },
              "event_type": {
                "type": "string",
                "enum": ["panel-update", "quiz", "hotspot", "chapter", "pause-prompt"],
                "description": "The type of event triggered at this timestamp."
              },
              "data": {
                "type": "object",
                "description": "Event payload. Structure depends on event_type.",
                "properties": {
                  "title": { "type": "string" },
                  "content": { "type": "string" },
                  "question": { "type": "string" },
                  "options": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "text": { "type": "string" },
                        "correct": { "type": "boolean" }
                      }
                    }
                  },
                  "hotspot_regions": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "x": { "type": "number" },
                        "y": { "type": "number" },
                        "width": { "type": "number" },
                        "height": { "type": "number" },
                        "label": { "type": "string" }
                      }
                    }
                  }
                }
              }
            }
          },
          "description": "Time-synced events triggered during video playback."
        },
        "allow_scrub": {
          "type": "boolean",
          "default": true,
          "description": "Whether the learner can scrub/seek through the video."
        },
        "require_events": {
          "type": "boolean",
          "default": false,
          "description": "If true, all quiz events must be answered before the block is considered complete."
        },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "simulation_block": {
      "type": "object",
      "description": "Simulated environment — software UI replica, process simulation, or resource management exercise.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "variant", "instruction"],
      "properties": {
        "type": { "const": "simulation" },
        "id": true,
        "variant": {
          "type": "string",
          "enum": ["software", "process", "resource", "role-play"],
          "description": "Simulation type. 'software' renders a UI replica; 'process' is a multi-step workflow; 'resource' involves allocation decisions; 'role-play' uses voice AI."
        },
        "instruction": {
          "type": "string",
          "description": "Task briefing explaining what the learner must accomplish."
        },
        "environment": {
          "type": "object",
          "description": "Simulation-specific configuration.",
          "properties": {
            "component_id": {
              "type": "string",
              "description": "ID of the React component implementing this simulation, for software simulations."
            },
            "initial_state": {
              "type": "object",
              "description": "Starting state for the simulation. Schema is simulation-specific."
            },
            "success_criteria": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["description", "check"],
                "properties": {
                  "description": { "type": "string", "description": "Human-readable success criterion." },
                  "check": { "type": "string", "description": "JSONPath or expression evaluated against simulation state to determine if criterion is met." }
                }
              },
              "description": "Conditions that must be met for the learner to pass."
            },
            "hints": {
              "type": "array",
              "items": { "type": "string" },
              "description": "Progressive hints revealed if the learner struggles. Shown one at a time."
            },
            "time_limit_seconds": {
              "type": "integer",
              "minimum": 0,
              "description": "Optional time limit. 0 or omitted means unlimited."
            },
            "voice_agent_id": {
              "type": "string",
              "description": "ElevenLabs voice agent ID for role-play simulations."
            }
          }
        },
        "feedback": { "$ref": "#/$defs/feedback_object" },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "dialogue_block": {
      "type": "object",
      "description": "Multi-character dialogue sequence. Characters speak in turns with optional learner interjections.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "characters", "lines"],
      "properties": {
        "type": { "const": "dialogue" },
        "id": true,
        "characters": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
              "id": { "type": "string", "description": "Character identifier referenced in lines." },
              "name": { "type": "string", "description": "Display name." },
              "voice_role": { "$ref": "#/$defs/voice_role" },
              "avatar": { "$ref": "#/$defs/media_ref", "description": "Character portrait image." },
              "role": { "type": "string", "description": "Character's role description, e.g. 'IT Security Lead'." }
            }
          },
          "description": "Characters participating in this dialogue."
        },
        "lines": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "object",
            "required": ["character_id"],
            "properties": {
              "character_id": { "type": "string", "description": "ID of the speaking character." },
              "text": { "type": "string", "description": "Spoken dialogue text." },
              "narration_text": { "type": "string", "description": "TTS text if different from display text." },
              "emotion": {
                "type": "string",
                "enum": ["neutral", "concerned", "excited", "frustrated", "thoughtful", "confident", "confused"],
                "default": "neutral",
                "description": "Emotional tone for avatar expression and TTS inflection."
              },
              "action": { "type": "string", "description": "Stage direction displayed as italicized text, e.g. '*leans forward*'." },
              "pause_ms": {
                "type": "integer",
                "minimum": 0,
                "description": "Pause in milliseconds before this line. Creates dramatic timing."
              },
              "learner_choice": {
                "type": "object",
                "description": "If present, the learner chooses what to say at this point in the dialogue.",
                "properties": {
                  "prompt": { "type": "string" },
                  "options": {
                    "type": "array",
                    "minItems": 2,
                    "items": {
                      "type": "object",
                      "required": ["text"],
                      "properties": {
                        "text": { "type": "string" },
                        "next_line_index": { "type": "integer", "description": "Index into the lines array to jump to. Omit to continue sequentially." },
                        "consequence": { "type": "string", "enum": ["good", "partial", "bad", "neutral"] },
                        "points": { "type": "integer", "minimum": 0 }
                      }
                    }
                  }
                },
                "required": ["options"]
              }
            }
          },
          "description": "Ordered sequence of dialogue lines."
        },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    },

    "code_playground_block": {
      "type": "object",
      "description": "In-browser coding exercise using Sandpack. Learner writes or modifies code with live preview.",
      "allOf": [{ "$ref": "#/$defs/base_block_properties" }],
      "required": ["type", "instruction", "template"],
      "properties": {
        "type": { "const": "code-playground" },
        "id": true,
        "instruction": {
          "type": "string",
          "description": "Task description explaining what the learner should code."
        },
        "template": {
          "type": "string",
          "enum": ["react", "react-ts", "vanilla", "vanilla-ts", "vue", "angular", "svelte", "node", "python", "static"],
          "description": "Sandpack template. Determines the runtime environment."
        },
        "files": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "required": ["code"],
            "properties": {
              "code": { "type": "string", "description": "File contents." },
              "hidden": { "type": "boolean", "default": false, "description": "If true, this file is not shown in the editor but exists in the sandbox." },
              "readOnly": { "type": "boolean", "default": false, "description": "If true, the learner cannot edit this file." },
              "active": { "type": "boolean", "default": false, "description": "If true, this file is initially open in the editor." }
            }
          },
          "description": "Map of file paths to file definitions. Keys are paths like '/App.tsx' or '/styles.css'."
        },
        "entry": {
          "type": "string",
          "description": "Entry file path. Defaults to the template's standard entry point."
        },
        "solution_files": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "code": { "type": "string" }
            }
          },
          "description": "Solution file contents. Revealed via a 'Show Solution' button."
        },
        "tests": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["description", "test_code"],
            "properties": {
              "description": { "type": "string", "description": "What this test checks." },
              "test_code": { "type": "string", "description": "JavaScript test code executed against the sandbox. Should return true/false or throw on failure." }
            }
          },
          "description": "Automated tests to validate the learner's code."
        },
        "dependencies": {
          "type": "object",
          "additionalProperties": { "type": "string" },
          "description": "Additional npm dependencies. Keys are package names, values are version specifiers."
        },
        "show_preview": {
          "type": "boolean",
          "default": true,
          "description": "Whether to show the live preview pane."
        },
        "show_console": {
          "type": "boolean",
          "default": false,
          "description": "Whether to show the console output pane."
        },
        "scoring": { "$ref": "#/$defs/scoring" },
        "narration": true,
        "narration_text": true,
        "voice_role": true,
        "background_audio": true,
        "image": true,
        "transition": true,
        "requires_completion": true
      },
      "additionalProperties": false
    }
  }
}
```

---

## Block Type Quick Reference

| Block Type | Purpose | Key Fields | Assessed? |
|------------|---------|------------|-----------|
| `narrative` | Exposition, scene-setting, storytelling | `text`, `heading`, `callout` | No |
| `branch` | Decision points with consequences | `prompt`, `choices[].consequence`, `choices[].next` | Yes |
| `knowledge-check` | Assessment questions (6 formats) | `question`, `format`, `options`/`items`/`hotspots` | Yes |
| `drag-drop` | Categorize, label, assemble, match | `variant`, `items`, `targets` | Yes |
| `hotspot` | Explore regions on an image | `hotspot_image`, `regions` | Optional |
| `scroll-story` | Scroll-driven narrative sections | `sections[].animation`, `show_progress_bar` | No |
| `interactive-video` | Video with time-synced events | `video`, `events[].time`, `events[].event_type` | Optional |
| `simulation` | Practice in replica environments | `variant`, `environment.success_criteria` | Yes |
| `dialogue` | Multi-character conversation | `characters`, `lines[].learner_choice` | Optional |
| `code-playground` | In-browser coding exercises | `template`, `files`, `tests` | Optional |

---

## Knowledge Check Format Reference

The `knowledge-check` block supports six question formats. Each format requires specific fields:

### single-choice

One correct answer from a list. The most common assessment format.

**Required fields:** `options` (with exactly one `correct: true`)
**Feedback structure:** `feedback.correct`, `feedback.incorrect`, optionally `feedback.partial`

### multi-choice

Multiple correct answers. Learner must select all correct options.

**Required fields:** `options` (with one or more `correct: true`)
**Feedback structure:** `feedback.correct`, `feedback.incorrect`, `feedback.partial`

### drag-drop-sort

Arrange items in the correct order.

**Required fields:** `items` (each with `text` and `correct_position`)
**Feedback structure:** `feedback.correct`, `feedback.incorrect`

### hotspot

Click specific regions on an image.

**Required fields:** `hotspot_image`, `hotspots`, `required_correct`
**Feedback structure:** `feedback.correct`, `feedback.incorrect`

### confidence-rated

Single-choice question with an added confidence self-assessment. Feedback varies based on both correctness and confidence.

**Required fields:** `options`, `confidence_prompt`, `confidence_levels`
**Feedback structure:** `feedback.correct_high_confidence`, `feedback.correct_low_confidence`, `feedback.incorrect_high_confidence`, `feedback.incorrect_low_confidence`

### free-response

Open-ended text response. Not auto-graded — uses rubric display and sample answers.

**Required fields:** `rubric`
**Optional fields:** `sample_answer`
**Feedback structure:** None (rubric serves as feedback reference)

---

## Complete Example content.json

This example demonstrates multiple block types in a single module for a cybersecurity awareness course.

```json
{
  "module": "02-email-threats",
  "title": "Recognizing Email-Based Threats",
  "objectives": [
    "Identify the five most common indicators of a phishing email",
    "Apply the SLAM method (Sender, Links, Attachments, Message) to evaluate suspicious emails",
    "Respond correctly to a business email compromise scenario within 60 seconds"
  ],
  "duration_minutes": 25,
  "prerequisite_modules": ["01-introduction"],
  "tags": ["security", "phishing", "email", "compliance", "intermediate"],
  "blocks": [
    {
      "type": "narrative",
      "id": "opening-scene",
      "heading": "Monday Morning",
      "text": "It's 8:47 AM. You've just settled in with your coffee when your inbox pings with three new messages. One is from your CEO, marked urgent. Another is from IT, asking you to verify your credentials. The third is a shipping notification from a package you don't remember ordering.\n\nAt least one of these is an attack. Maybe all three.",
      "narration_text": "It's 8:47 AM. You've just settled in with your coffee when your inbox pings. Three new messages. One from your CEO, marked urgent. Another from IT. And a shipping notification you weren't expecting. Here's the thing — at least one of these is an attack. Maybe all three.",
      "voice_role": "narrator",
      "background_audio": "ambient-office",
      "image": {
        "src": "media/inbox-morning.png",
        "alt": "Email inbox showing three unread messages: an urgent CEO request, an IT verification notice, and a shipping notification"
      },
      "transition": "fade"
    },
    {
      "type": "scroll-story",
      "id": "slam-method",
      "sections": [
        {
          "id": "slam-intro",
          "title": "The SLAM Method",
          "content": "Security professionals use a four-point check called **SLAM** to evaluate every suspicious email. It takes 30 seconds and catches 95% of phishing attempts.",
          "visual": { "src": "media/slam-overview.svg", "alt": "SLAM acronym diagram showing Sender, Links, Attachments, Message" },
          "animation": "fade-up",
          "narration_text": "Security professionals use a four-point check to evaluate suspicious emails. It's called SLAM, and it takes about 30 seconds.",
          "voice_role": "narrator"
        },
        {
          "id": "slam-sender",
          "title": "S — Sender",
          "content": "Check the actual email address, not just the display name. Hover over the sender to reveal the real address. Look for:\n- Misspelled domains (g00gle.com, micros0ft.com)\n- Lookalike characters (rn looks like m in some fonts)\n- Free email services for 'corporate' messages",
          "visual": { "src": "media/sender-comparison.png", "alt": "Side-by-side comparison of a legitimate sender address versus a spoofed one with a zero replacing the letter O" },
          "animation": "slide-left"
        },
        {
          "id": "slam-links",
          "title": "L — Links",
          "content": "Hover before you click. The displayed text and the actual URL are often completely different. Check for:\n- HTTP instead of HTTPS\n- Domains that don't match the claimed sender\n- URL shorteners hiding the real destination\n- Typosquatted domains",
          "visual": { "src": "media/link-hover-reveal.png", "alt": "Mouse hovering over a link showing the tooltip reveals a completely different URL than the displayed text" },
          "animation": "slide-left"
        },
        {
          "id": "slam-attachments",
          "title": "A — Attachments",
          "content": "Unexpected attachments are the primary malware delivery mechanism. Be especially wary of:\n- ZIP files (hide contents from scanners)\n- Office documents with macros (.docm, .xlsm)\n- Executable files disguised with double extensions (report.pdf.exe)\n- Password-protected files (designed to bypass scanning)",
          "visual": { "src": "media/dangerous-attachments.svg", "alt": "Icons showing dangerous file types: ZIP, DOCM, EXE disguised as PDF" },
          "animation": "slide-left"
        },
        {
          "id": "slam-message",
          "title": "M — Message",
          "content": "Read the message content critically. Phishing emails almost always use psychological pressure:\n- **Urgency**: 'Act now or your account will be locked'\n- **Authority**: 'The CEO needs this immediately'\n- **Fear**: 'Unusual login detected on your account'\n- **Curiosity**: 'You won't believe what was said about you'",
          "visual": { "src": "media/pressure-tactics.svg", "alt": "Four icons representing urgency, authority, fear, and curiosity manipulation tactics" },
          "animation": "slide-left"
        }
      ],
      "show_progress_bar": true,
      "background_audio": "ambient-learning"
    },
    {
      "type": "knowledge-check",
      "id": "slam-recall",
      "question": "What does the 'L' in the SLAM method stand for?",
      "format": "single-choice",
      "options": [
        { "text": "Legitimacy", "correct": false },
        { "text": "Links", "correct": true },
        { "text": "Language", "correct": false },
        { "text": "Logging", "correct": false }
      ],
      "feedback": {
        "correct": "Right — always hover over links to verify the actual URL before clicking.",
        "incorrect": "The 'L' stands for Links. Hovering over links to check their true destination is one of the most effective phishing defenses."
      },
      "difficulty": "beginner",
      "bloom_level": "remember",
      "scoring": {
        "points": 10,
        "attempts_allowed": 2,
        "objective_ids": ["identify-phishing-indicators"]
      }
    },
    {
      "type": "hotspot",
      "id": "phishing-analysis",
      "instruction": "Examine this email carefully. Click on every element that indicates this is a phishing attempt. Find all five red flags.",
      "hotspot_image": {
        "src": "media/phishing-email-full.png",
        "alt": "A realistic-looking email from 'IT Department' asking the user to verify their credentials via a link"
      },
      "regions": [
        {
          "id": "sender-address",
          "x": 110,
          "y": 42,
          "width": 220,
          "height": 18,
          "shape": "rect",
          "label": "Sender email address",
          "content": "The sender shows 'IT Department' but the actual address is it-support@company-verify.com — not your company's real domain.",
          "narration_text": "Look at the actual email address. I T support at company dash verify dot com. That's not your company's domain.",
          "voice_role": "mentor"
        },
        {
          "id": "urgency-language",
          "x": 50,
          "y": 120,
          "width": 400,
          "height": 24,
          "shape": "rect",
          "label": "Urgent language in subject line",
          "content": "'IMMEDIATE ACTION REQUIRED' — urgency is the most common pressure tactic in phishing. Legitimate IT departments don't threaten account deletion within 24 hours.",
          "narration_text": "Immediate action required. This kind of manufactured urgency is the number one pressure tactic in phishing. Real I T departments don't threaten to delete your account in 24 hours.",
          "voice_role": "mentor"
        },
        {
          "id": "generic-greeting",
          "x": 50,
          "y": 160,
          "width": 150,
          "height": 20,
          "shape": "rect",
          "label": "Generic greeting",
          "content": "'Dear User' — your company's IT team knows your name. Generic greetings indicate a mass-sent phishing campaign.",
          "voice_role": "mentor"
        },
        {
          "id": "suspicious-link",
          "x": 130,
          "y": 250,
          "width": 200,
          "height": 18,
          "shape": "rect",
          "label": "Suspicious verification link",
          "content": "The button says 'Verify Now' but hovering reveals it points to http://company-verify.com/login — an HTTP site (not HTTPS) on a lookalike domain.",
          "voice_role": "mentor"
        },
        {
          "id": "threat-language",
          "x": 50,
          "y": 290,
          "width": 450,
          "height": 20,
          "shape": "rect",
          "label": "Threatening consequence",
          "content": "'Failure to verify will result in permanent account suspension' — threat of loss is a fear-based manipulation technique.",
          "voice_role": "mentor"
        }
      ],
      "require_all": true,
      "requires_completion": true,
      "background_audio": "scenario-tension"
    },
    {
      "type": "dialogue",
      "id": "colleague-chat",
      "characters": [
        {
          "id": "alex",
          "name": "Alex Rivera",
          "role": "Your colleague",
          "voice_role": "character-1",
          "avatar": { "src": "media/avatar-alex.png", "alt": "Alex Rivera, a colleague wearing a blue collared shirt" }
        },
        {
          "id": "you",
          "name": "You",
          "role": "Employee",
          "voice_role": "learner"
        }
      ],
      "lines": [
        {
          "character_id": "alex",
          "text": "Hey, did you get that email from IT about verifying your credentials? I just clicked the link and logged in. Seemed legit.",
          "emotion": "neutral"
        },
        {
          "character_id": "alex",
          "text": "Wait — you look worried. What's wrong?",
          "emotion": "confused",
          "pause_ms": 1500
        },
        {
          "character_id": "you",
          "text": "",
          "learner_choice": {
            "prompt": "How do you respond to Alex?",
            "options": [
              {
                "text": "Alex, that was a phishing email. You need to change your password right now and report this to IT security.",
                "consequence": "good",
                "points": 20,
                "next_line_index": 3
              },
              {
                "text": "I'm not sure, but something felt off about it. The domain looked wrong.",
                "consequence": "partial",
                "points": 10,
                "next_line_index": 5
              },
              {
                "text": "Oh, I haven't checked my email yet. I'll look at it later.",
                "consequence": "bad",
                "points": 0,
                "next_line_index": 7
              }
            ]
          }
        },
        {
          "character_id": "alex",
          "text": "Phishing? Really? It looked exactly like the emails IT usually sends...",
          "emotion": "concerned"
        },
        {
          "character_id": "alex",
          "text": "OK, changing my password now. Thanks for the heads up — I'll call the security team right away.",
          "emotion": "concerned",
          "action": "*opens password reset page*"
        },
        {
          "character_id": "alex",
          "text": "The domain? What do you mean?",
          "emotion": "confused"
        },
        {
          "character_id": "alex",
          "text": "Oh no — you're right. It says company-verify.com, not our actual domain. I need to change my password...",
          "emotion": "frustrated",
          "action": "*frantically opens password settings*"
        },
        {
          "character_id": "alex",
          "text": "OK, suit yourself. I'm sure it's fine.",
          "emotion": "neutral"
        }
      ],
      "scoring": {
        "points": 20,
        "passing_fraction": 0.5,
        "objective_ids": ["respond-to-bec-scenario"]
      },
      "background_audio": "ambient-office"
    },
    {
      "type": "branch",
      "id": "ceo-wire-transfer",
      "prompt": "An email arrives from your CEO: 'I need you to wire $50,000 to a new vendor urgently. Use the attached bank details. This is confidential — don't discuss with anyone else.' What do you do?",
      "context": "You've just finished analyzing the IT phishing email when another urgent message appears. This one appears to come from Jordan Park, your CEO.",
      "choices": [
        {
          "text": "Forward to accounting with instructions to process the transfer",
          "consequence": "bad",
          "feedback": "This is exactly what the attacker hoped for. Business email compromise (BEC) cost organizations $2.7 billion last year. The 'confidential' instruction is designed to prevent you from verifying through normal channels.",
          "next": "consequence-bad-wire",
          "points": 0
        },
        {
          "text": "Call the CEO directly on their known phone number to verify",
          "consequence": "good",
          "feedback": "Excellent. Out-of-band verification — contacting someone through a different channel than the one the request came on — is the single most effective defense against BEC. The attacker controls the email channel but cannot intercept a phone call.",
          "next": "consequence-good-verify",
          "points": 30
        },
        {
          "text": "Reply to the email asking for more details",
          "consequence": "bad",
          "feedback": "The attacker controls the email thread. Replying keeps you in their channel. Any response you get will be crafted to increase pressure and overcome your hesitation.",
          "next": "consequence-bad-reply",
          "points": 0
        },
        {
          "text": "Check the sender's email address and headers",
          "consequence": "partial",
          "feedback": "Good instinct, but insufficient on its own. Sophisticated BEC attacks use compromised legitimate accounts or nearly identical domains. Even if the address looks right, you should still verify out-of-band for any unusual financial request.",
          "next": "consequence-partial-check",
          "points": 10
        }
      ],
      "scoring": {
        "points": 30,
        "passing_fraction": 0.5,
        "objective_ids": ["respond-to-bec-scenario"]
      },
      "narration_text": "A new email appears in your inbox. It's from Jordan Park, your CEO. Urgent, confidential, and asking you to wire fifty thousand dollars to a new vendor. What do you do?",
      "voice_role": "narrator",
      "background_audio": "scenario-tension",
      "image": {
        "src": "media/ceo-email.png",
        "alt": "Email from CEO Jordan Park requesting an urgent wire transfer of $50,000 to a new vendor, marked confidential"
      }
    },
    {
      "type": "knowledge-check",
      "id": "verification-method",
      "question": "Which verification method is most effective against business email compromise?",
      "format": "confidence-rated",
      "options": [
        { "text": "Checking the email header for anomalies", "correct": false },
        { "text": "Out-of-band verification (calling on a known number)", "correct": true },
        { "text": "Replying to the email to confirm the request", "correct": false },
        { "text": "Forwarding to a colleague for a second opinion", "correct": false }
      ],
      "confidence_prompt": "How confident are you in this answer?",
      "confidence_levels": ["Guessing", "Somewhat confident", "Very confident"],
      "feedback": {
        "correct_high_confidence": "Exactly right, and you knew it. Out-of-band verification breaks the attacker's control over the communication channel. This is the gold standard for verifying unusual requests.",
        "correct_low_confidence": "You got it right — trust your instincts here. Out-of-band verification is the gold standard because the attacker cannot intercept a phone call to a known number.",
        "incorrect_high_confidence": "This is worth correcting because you were confident. The answer is out-of-band verification — contacting the person through a completely different channel (phone, in-person). The attacker may control the email channel, even the headers.",
        "incorrect_low_confidence": "Good that you flagged your uncertainty. The most effective method is out-of-band verification — calling the person on their known phone number. This breaks the attacker's control over the conversation."
      },
      "difficulty": "intermediate",
      "bloom_level": "evaluate",
      "scoring": {
        "points": 15,
        "attempts_allowed": 1,
        "objective_ids": ["respond-to-bec-scenario"]
      }
    },
    {
      "type": "drag-drop",
      "id": "categorize-threats",
      "variant": "categorize",
      "instruction": "Drag each example into the correct email threat category.",
      "items": [
        { "id": "item-1", "content": "Email from 'CEO' requesting urgent wire transfer", "target_id": "bec" },
        { "id": "item-2", "content": "Link to fake login page mimicking your company portal", "target_id": "credential-phishing" },
        { "id": "item-3", "content": "Attachment named 'Invoice.pdf.exe'", "target_id": "malware" },
        { "id": "item-4", "content": "Email threatening account closure unless you verify identity", "target_id": "credential-phishing" },
        { "id": "item-5", "content": "Request from 'HR' to update direct deposit to a new account", "target_id": "bec" },
        { "id": "item-6", "content": "Macro-enabled spreadsheet claiming to be a delivery receipt", "target_id": "malware" }
      ],
      "targets": [
        { "id": "bec", "label": "Business Email Compromise" },
        { "id": "credential-phishing", "label": "Credential Phishing" },
        { "id": "malware", "label": "Malware Delivery" }
      ],
      "feedback": {
        "correct": "Perfect classification. Recognizing the attack type helps you apply the right defense — out-of-band verification for BEC, link inspection for credential phishing, and attachment caution for malware delivery.",
        "incorrect": "Review the categories: BEC impersonates authority figures requesting actions (money, data). Credential phishing steals login details via fake pages. Malware delivery uses infected attachments."
      },
      "scoring": {
        "points": 20,
        "passing_fraction": 0.7,
        "attempts_allowed": 2,
        "penalty_per_retry": 0.25,
        "objective_ids": ["identify-phishing-indicators"]
      },
      "requires_completion": true
    },
    {
      "type": "knowledge-check",
      "id": "incident-response-order",
      "question": "Your colleague just clicked a phishing link and entered their password. Order these response steps correctly:",
      "format": "drag-drop-sort",
      "items": [
        { "text": "Have the colleague change their password immediately", "correct_position": 1 },
        { "text": "Report the incident to IT security", "correct_position": 2 },
        { "text": "Check for unauthorized access to the account", "correct_position": 3 },
        { "text": "Alert other employees who may have received the same email", "correct_position": 4 },
        { "text": "Document what happened for the incident report", "correct_position": 5 }
      ],
      "feedback": {
        "correct": "Correct sequence. The priority is stopping ongoing damage (password change), then escalating (IT security), then investigating (access check), then preventing spread (alerting others), and finally documenting.",
        "incorrect": "The correct priority order is: 1) Change password (stop the bleeding), 2) Report to IT security (escalate), 3) Check for unauthorized access (investigate), 4) Alert others (prevent spread), 5) Document (learn). Containment always comes before documentation."
      },
      "difficulty": "intermediate",
      "bloom_level": "apply",
      "scoring": {
        "points": 15,
        "passing_fraction": 0.6,
        "objective_ids": ["respond-to-bec-scenario"]
      }
    },
    {
      "type": "interactive-video",
      "id": "real-world-examples",
      "video": {
        "src": "media/phishing-in-the-wild.mp4",
        "caption_src": "media/phishing-in-the-wild.vtt",
        "duration_seconds": 240
      },
      "events": [
        {
          "time": 0,
          "event_type": "chapter",
          "data": { "title": "Introduction" }
        },
        {
          "time": 15,
          "event_type": "panel-update",
          "data": {
            "title": "The Target CEO Scam (2019)",
            "content": "A UK energy firm's CEO was tricked by an AI-generated voice deepfake into wiring $243,000. The voice perfectly mimicked his boss's German accent and speech patterns."
          }
        },
        {
          "time": 60,
          "event_type": "chapter",
          "data": { "title": "Evolution of Phishing" }
        },
        {
          "time": 90,
          "event_type": "quiz",
          "data": {
            "question": "What made this voice-based attack different from traditional phishing?",
            "options": [
              { "text": "It used a phone call instead of email", "correct": false },
              { "text": "It used AI to clone the boss's actual voice", "correct": true },
              { "text": "It targeted a CEO instead of a regular employee", "correct": false }
            ]
          }
        },
        {
          "time": 150,
          "event_type": "chapter",
          "data": { "title": "Defense Strategies" }
        },
        {
          "time": 200,
          "event_type": "pause-prompt",
          "data": {
            "title": "Think About It",
            "content": "If AI can now clone voices convincingly, what verification methods still work? Think about this before continuing."
          }
        }
      ],
      "allow_scrub": true,
      "require_events": true,
      "background_audio": "ambient-learning"
    },
    {
      "type": "code-playground",
      "id": "email-header-parser",
      "instruction": "Write a function that parses an email header and returns an object with sender, return-path, and authentication results. This is a simplified version of what email security tools do automatically.\n\nComplete the `parseEmailHeader` function so all tests pass.",
      "template": "vanilla-ts",
      "files": {
        "/index.ts": {
          "code": "interface EmailHeaderInfo {\n  from: string;\n  returnPath: string;\n  spfResult: 'pass' | 'fail' | 'none';\n  dkimResult: 'pass' | 'fail' | 'none';\n  mismatch: boolean;\n}\n\nexport function parseEmailHeader(rawHeader: string): EmailHeaderInfo {\n  // TODO: Parse the raw email header string\n  // Each line is in the format \"Key: Value\"\n  // Lines:\n  //   From: display name <email>\n  //   Return-Path: <email>\n  //   Authentication-Results: spf=pass/fail; dkim=pass/fail\n  // Set mismatch to true if From email domain !== Return-Path domain\n  \n  return {\n    from: '',\n    returnPath: '',\n    spfResult: 'none',\n    dkimResult: 'none',\n    mismatch: false,\n  };\n}\n\n// Test it\nconst header = `From: Jordan Park <jordan@company.com>\nReturn-Path: <jordan@c0mpany.com>\nAuthentication-Results: spf=fail; dkim=fail`;\n\nconst result = parseEmailHeader(header);\nconsole.log(result);\nconsole.log('Mismatch detected:', result.mismatch);",
          "active": true
        }
      },
      "solution_files": {
        "/index.ts": {
          "code": "interface EmailHeaderInfo {\n  from: string;\n  returnPath: string;\n  spfResult: 'pass' | 'fail' | 'none';\n  dkimResult: 'pass' | 'fail' | 'none';\n  mismatch: boolean;\n}\n\nexport function parseEmailHeader(rawHeader: string): EmailHeaderInfo {\n  const lines = rawHeader.split('\\n');\n  const info: EmailHeaderInfo = {\n    from: '',\n    returnPath: '',\n    spfResult: 'none',\n    dkimResult: 'none',\n    mismatch: false,\n  };\n\n  for (const line of lines) {\n    if (line.startsWith('From:')) {\n      const match = line.match(/<(.+)>/);\n      info.from = match ? match[1] : line.replace('From:', '').trim();\n    } else if (line.startsWith('Return-Path:')) {\n      const match = line.match(/<(.+)>/);\n      info.returnPath = match ? match[1] : line.replace('Return-Path:', '').trim();\n    } else if (line.startsWith('Authentication-Results:')) {\n      const authLine = line.replace('Authentication-Results:', '').trim();\n      const spfMatch = authLine.match(/spf=(pass|fail)/);\n      const dkimMatch = authLine.match(/dkim=(pass|fail)/);\n      if (spfMatch) info.spfResult = spfMatch[1] as 'pass' | 'fail';\n      if (dkimMatch) info.dkimResult = dkimMatch[1] as 'pass' | 'fail';\n    }\n  }\n\n  const fromDomain = info.from.split('@')[1];\n  const returnDomain = info.returnPath.split('@')[1];\n  info.mismatch = fromDomain !== returnDomain;\n\n  return info;\n}\n\nconst header = `From: Jordan Park <jordan@company.com>\nReturn-Path: <jordan@c0mpany.com>\nAuthentication-Results: spf=fail; dkim=fail`;\n\nconst result = parseEmailHeader(header);\nconsole.log(result);\nconsole.log('Mismatch detected:', result.mismatch);"
        }
      },
      "tests": [
        {
          "description": "Extracts the From email address from angle brackets",
          "test_code": "const r = parseEmailHeader('From: Test <a@b.com>\\nReturn-Path: <a@b.com>\\nAuthentication-Results: spf=pass; dkim=pass'); return r.from === 'a@b.com';"
        },
        {
          "description": "Detects domain mismatch between From and Return-Path",
          "test_code": "const r = parseEmailHeader('From: Boss <a@real.com>\\nReturn-Path: <a@fake.com>\\nAuthentication-Results: spf=fail; dkim=fail'); return r.mismatch === true;"
        },
        {
          "description": "Parses SPF and DKIM results",
          "test_code": "const r = parseEmailHeader('From: X <a@b.com>\\nReturn-Path: <a@b.com>\\nAuthentication-Results: spf=fail; dkim=pass'); return r.spfResult === 'fail' && r.dkimResult === 'pass';"
        }
      ],
      "show_preview": false,
      "show_console": true,
      "scoring": {
        "points": 25,
        "passing_fraction": 1.0,
        "objective_ids": ["identify-phishing-indicators"]
      },
      "narration_text": "Let's get hands-on. You're going to write a simplified email header parser — the same kind of logic that real email security tools use to detect spoofed senders.",
      "voice_role": "mentor",
      "requires_completion": true
    },
    {
      "type": "simulation",
      "id": "email-triage",
      "variant": "software",
      "instruction": "You have five emails in your inbox. Apply the SLAM method to each one. Mark each email as Safe, Suspicious, or Phishing. You must correctly classify at least four of the five to pass.",
      "environment": {
        "component_id": "EmailTriageSimulation",
        "initial_state": {
          "emails": [
            { "id": "email-1", "classification": null },
            { "id": "email-2", "classification": null },
            { "id": "email-3", "classification": null },
            { "id": "email-4", "classification": null },
            { "id": "email-5", "classification": null }
          ],
          "submitted": false
        },
        "success_criteria": [
          {
            "description": "Correctly classified at least 4 of 5 emails",
            "check": "$.emails.filter(e => e.classification === e.correct_classification).length >= 4"
          }
        ],
        "hints": [
          "Remember to check the sender's actual email address, not just the display name.",
          "Hover over any links in the email body to see where they really point.",
          "Look for urgency language — legitimate senders rarely demand immediate action.",
          "Check whether the email addresses you by name or uses a generic greeting."
        ],
        "time_limit_seconds": 300
      },
      "feedback": {
        "correct": "Strong work. You correctly triaged the inbox using the SLAM method. In a real environment, reporting suspicious emails to IT security creates a feedback loop that improves your organization's defenses.",
        "incorrect": "Some of those were tricky. Review the SLAM method — Sender, Links, Attachments, Message — and try again. Pay special attention to the email addresses and link destinations."
      },
      "scoring": {
        "points": 30,
        "passing_fraction": 0.8,
        "attempts_allowed": 3,
        "penalty_per_retry": 0.2,
        "objective_ids": ["identify-phishing-indicators", "apply-slam-method"]
      },
      "requires_completion": true,
      "background_audio": "scenario-tension"
    },
    {
      "type": "knowledge-check",
      "id": "final-free-response",
      "question": "Describe a situation where checking the sender's email address alone would NOT be sufficient to identify a phishing attempt. What additional steps would you take?",
      "format": "free-response",
      "rubric": "Strong answers will: (1) Identify a specific scenario such as a compromised legitimate account or a convincing lookalike domain, (2) Explain why email address verification fails in that case, (3) Describe at least two additional verification steps such as out-of-band verification, checking authentication headers, or contacting IT security.",
      "sample_answer": "If an attacker compromises a colleague's actual email account through credential theft, every email they send will come from a legitimate address. The sender check passes completely. In this case, I would look for behavioral anomalies (unusual requests, different writing style, odd timing), verify any sensitive requests through a phone call to the person's known number, and check whether the email's content matches what that person would normally send. I would also report anything suspicious to IT security so they can check for signs of account compromise.",
      "difficulty": "advanced",
      "bloom_level": "evaluate",
      "scoring": {
        "points": 20,
        "objective_ids": ["identify-phishing-indicators", "apply-slam-method"]
      },
      "narration_text": "One last question. This one requires you to think critically about the limits of what we've covered today.",
      "voice_role": "narrator"
    },
    {
      "type": "narrative",
      "id": "module-summary",
      "heading": "Module Summary",
      "text": "You've learned to recognize email-based threats using the SLAM method — checking the **S**ender, **L**inks, **A**ttachments, and **M**essage content. You practiced identifying phishing indicators, responding to a business email compromise scenario, and classifying different types of email attacks.\n\nThe most important takeaway: **when in doubt, verify through a different channel.** A 30-second phone call can prevent a million-dollar loss.",
      "callout": {
        "type": "tip",
        "text": "Make SLAM a habit. The more you practice, the faster it becomes — until checking emails critically is automatic."
      },
      "narration_text": "That wraps up this module. Remember the SLAM method. And when something feels off, pick up the phone. A thirty-second call can prevent a catastrophic loss.",
      "voice_role": "narrator",
      "background_audio": "reflection",
      "transition": "fade"
    }
  ]
}
```

---

## Validation Guidance

### Installing the Schema Validator

Use [ajv](https://ajv.js.org/) (Another JSON Validator) with the JSON Schema 2020-12 draft support.

```bash
npm install ajv ajv-formats --save-dev
```

### Validation Script

Create a build-pipeline script that validates all module content files before the course is built.

```typescript
// scripts/validate-content.ts
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { readFileSync, readdirSync, statSync } from "fs";
import { join, relative } from "path";

// Load the schema
const schema = JSON.parse(
  readFileSync(join(__dirname, "../schemas/module-content.schema.json"), "utf-8")
);

// Initialize ajv with 2020-12 draft support
const ajv = new Ajv2020({
  allErrors: true,       // Report all errors, not just the first
  verbose: true,         // Include data in error messages
  strict: false,         // Allow schema features like `true` property values
});
addFormats(ajv);

const validate = ajv.compile(schema);

// Find all content.json files
function findContentFiles(dir: string): string[] {
  const files: string[] = [];
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    if (statSync(fullPath).isDirectory()) {
      files.push(...findContentFiles(fullPath));
    } else if (entry === "content.json") {
      files.push(fullPath);
    }
  }
  return files;
}

// Validate all modules
const modulesDir = join(__dirname, "../content/modules");
const contentFiles = findContentFiles(modulesDir);

let hasErrors = false;

for (const filePath of contentFiles) {
  const moduleName = relative(modulesDir, filePath);
  const data = JSON.parse(readFileSync(filePath, "utf-8"));

  const valid = validate(data);

  if (valid) {
    console.log(`  PASS  ${moduleName}`);
  } else {
    hasErrors = true;
    console.error(`  FAIL  ${moduleName}`);
    for (const error of validate.errors ?? []) {
      console.error(`         ${error.instancePath || "/"}: ${error.message}`);
      if (error.params) {
        console.error(`         params: ${JSON.stringify(error.params)}`);
      }
    }
  }
}

if (hasErrors) {
  console.error("\nContent validation failed. Fix errors before building.");
  process.exit(1);
} else {
  console.log(`\nAll ${contentFiles.length} module(s) passed validation.`);
}
```

### Semantic Validation

JSON Schema validates structure but cannot catch all logic errors. Add these semantic checks after schema validation passes.

```typescript
// scripts/validate-content-semantics.ts

interface SemanticError {
  block_id: string;
  message: string;
  severity: "error" | "warning";
}

function validateSemantics(module: any): SemanticError[] {
  const errors: SemanticError[] = [];
  const blockIds = new Set<string>();

  for (const block of module.blocks) {
    // 1. Check for duplicate block IDs
    if (block.id) {
      if (blockIds.has(block.id)) {
        errors.push({
          block_id: block.id,
          message: `Duplicate block ID: "${block.id}"`,
          severity: "error",
        });
      }
      blockIds.add(block.id);
    }

    // 2. Branch blocks: verify 'next' targets exist
    if (block.type === "branch") {
      for (const choice of block.choices) {
        if (choice.next && !module.blocks.some((b: any) => b.id === choice.next)) {
          errors.push({
            block_id: block.id,
            message: `Branch choice references non-existent block: "${choice.next}"`,
            severity: "error",
          });
        }
      }
    }

    // 3. Knowledge checks: format-specific field validation
    if (block.type === "knowledge-check") {
      switch (block.format) {
        case "single-choice": {
          const correctCount = block.options?.filter((o: any) => o.correct).length ?? 0;
          if (correctCount !== 1) {
            errors.push({
              block_id: block.id,
              message: `single-choice question must have exactly 1 correct option, found ${correctCount}`,
              severity: "error",
            });
          }
          break;
        }
        case "multi-choice": {
          const correctCount = block.options?.filter((o: any) => o.correct).length ?? 0;
          if (correctCount < 1) {
            errors.push({
              block_id: block.id,
              message: `multi-choice question must have at least 1 correct option`,
              severity: "error",
            });
          }
          break;
        }
        case "drag-drop-sort": {
          if (!block.items || block.items.length === 0) {
            errors.push({
              block_id: block.id,
              message: `drag-drop-sort question requires items array`,
              severity: "error",
            });
          }
          break;
        }
        case "hotspot": {
          if (!block.hotspots || !block.hotspot_image) {
            errors.push({
              block_id: block.id,
              message: `hotspot question requires hotspot_image and hotspots`,
              severity: "error",
            });
          }
          break;
        }
        case "confidence-rated": {
          if (!block.confidence_prompt || !block.confidence_levels) {
            errors.push({
              block_id: block.id,
              message: `confidence-rated question requires confidence_prompt and confidence_levels`,
              severity: "error",
            });
          }
          break;
        }
        case "free-response": {
          if (!block.rubric) {
            errors.push({
              block_id: block.id,
              message: `free-response question requires rubric`,
              severity: "error",
            });
          }
          break;
        }
      }
    }

    // 4. Dialogue blocks: verify character references
    if (block.type === "dialogue") {
      const characterIds = new Set(block.characters.map((c: any) => c.id));
      for (const line of block.lines) {
        if (!characterIds.has(line.character_id)) {
          errors.push({
            block_id: block.id,
            message: `Dialogue line references unknown character: "${line.character_id}"`,
            severity: "error",
          });
        }
      }
    }

    // 5. Drag-drop blocks: verify item target references
    if (block.type === "drag-drop") {
      const targetIds = new Set(block.targets.map((t: any) => t.id));
      for (const item of block.items) {
        if (!targetIds.has(item.target_id)) {
          errors.push({
            block_id: block.id,
            message: `Drag-drop item "${item.id}" references unknown target: "${item.target_id}"`,
            severity: "error",
          });
        }
      }
    }

    // 6. Scoring objective coverage: warn if objectives aren't assessed
    if (block.scoring?.objective_ids) {
      // Collect for cross-reference (handled in a second pass)
    }

    // 7. Narration text without voice role
    if (block.narration_text && !block.voice_role) {
      errors.push({
        block_id: block.id ?? "(unnamed block)",
        message: `Block has narration_text but no voice_role — TTS pipeline won't know which voice to use`,
        severity: "warning",
      });
    }
  }

  // 8. Check objective coverage — every module objective should be assessed
  const assessedObjectives = new Set<string>();
  for (const block of module.blocks) {
    if (block.scoring?.objective_ids) {
      for (const id of block.scoring.objective_ids) {
        assessedObjectives.add(id);
      }
    }
  }
  // This is a warning rather than an error since objective IDs in the module
  // are prose strings that don't have machine-parseable IDs yet.

  return errors;
}
```

### Integration with the Build Pipeline

Add validation as a pre-build step in `package.json`:

```json
{
  "scripts": {
    "validate": "tsx scripts/validate-content.ts && tsx scripts/validate-content-semantics.ts",
    "prebuild": "npm run validate",
    "build": "vite build",
    "build-course": "npm run build && npm run generate-manifest && npm run package-scorm"
  }
}
```

This ensures that `npm run build` or `npm run build-course` will fail fast if any content file is malformed, before Vite even starts bundling.

### CI Integration

```yaml
# .github/workflows/validate-content.yml
name: Validate Course Content
on:
  pull_request:
    paths:
      - "content/**/*.json"
      - "schemas/**"
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run validate
```

### Schema Distribution

Store the schema file alongside the course code so both agents and the player reference the same contract:

```
my-course/
├── schemas/
│   └── module-content.schema.json    # The schema from this document
├── content/
│   └── modules/
│       ├── 01-introduction/
│       │   └── content.json          # Validated against the schema
│       └── 02-email-threats/
│           └── content.json
└── scripts/
    ├── validate-content.ts           # Schema validation
    └── validate-content-semantics.ts # Logic validation
```

When generating content, agents should be provided the schema as context so they produce valid output on the first pass. The validation scripts serve as a safety net, not the primary quality mechanism.
