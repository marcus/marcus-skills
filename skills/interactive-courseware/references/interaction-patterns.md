# Interaction Patterns Reference

Implementation details for courseware interactions that drive engagement.

## Branching Scenarios

### Content Format

```json
{
  "type": "scenario",
  "id": "phishing-response",
  "title": "The Suspicious Email",
  "characters": [
    { "id": "narrator", "name": "Narrator", "voice": "narrator" },
    { "id": "alex", "name": "Alex Chen", "voice": "learner", "role": "You (IT Manager)" },
    { "id": "ceo", "name": "Jordan Park", "voice": "mentor", "role": "CEO" }
  ],
  "scenes": [
    {
      "id": "opening",
      "narration": "It's Monday morning. You're reviewing your inbox when you notice an urgent email from Jordan, the CEO.",
      "background": "office-morning",
      "elements": [
        { "type": "email-preview", "from": "Jordan Park <j.park@c0mpany.com>", "subject": "URGENT: Wire Transfer Needed" }
      ],
      "choices": [
        { "text": "Open the email", "next": "read-email" },
        { "text": "Check the sender address first", "next": "check-address", "points": 10 }
      ]
    },
    {
      "id": "check-address",
      "narration": "Good instinct. You hover over the sender name and notice the domain is c0mpany.com — with a zero instead of the letter O.",
      "feedback": { "type": "positive", "text": "Checking sender addresses is a strong first step, but sophisticated attacks use convincing lookalike domains." },
      "choices": [
        { "text": "Report to IT security immediately", "next": "report-good", "points": 20 },
        { "text": "Open it anyway to see what they want", "next": "read-email" },
        { "text": "Delete and ignore it", "next": "delete-partial", "points": 5 }
      ]
    }
  ],
  "scoring": {
    "max_points": 100,
    "passing_score": 60,
    "rubric": {
      "security_awareness": { "weight": 0.4 },
      "protocol_compliance": { "weight": 0.3 },
      "communication": { "weight": 0.3 }
    }
  }
}
```

### React Component Pattern

```tsx
// interactions/BranchingScenario.tsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Scene {
  id: string;
  narration?: string;
  background?: string;
  elements?: Array<{ type: string; [key: string]: unknown }>;
  feedback?: { type: string; text: string };
  choices: Array<{ text: string; next: string; points?: number }>;
}

interface ScenarioProps {
  scenes: Scene[];
  onComplete: (score: number, maxScore: number, path: string[]) => void;
}

export function BranchingScenario({ scenes, onComplete }: ScenarioProps) {
  const [currentSceneId, setCurrentSceneId] = useState(scenes[0].id);
  const [score, setScore] = useState(0);
  const [path, setPath] = useState<string[]>([scenes[0].id]);
  const [showFeedback, setShowFeedback] = useState(false);

  const scene = scenes.find(s => s.id === currentSceneId);
  if (!scene) return null;

  function handleChoice(choice: typeof scene.choices[0]) {
    if (choice.points) setScore(s => s + choice.points);
    setPath(p => [...p, choice.next]);

    const nextScene = scenes.find(s => s.id === choice.next);
    if (!nextScene) {
      // End of scenario
      onComplete(score + (choice.points || 0), 100, [...path, choice.next]);
      return;
    }

    if (nextScene.feedback) {
      setShowFeedback(true);
      setTimeout(() => {
        setShowFeedback(false);
        setCurrentSceneId(choice.next);
      }, 3000);
    } else {
      setCurrentSceneId(choice.next);
    }
  }

  return (
    <div className="scenario" role="region" aria-label="Interactive scenario">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentSceneId}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {scene.narration && (
            <p className="narration" aria-live="polite">{scene.narration}</p>
          )}

          {scene.feedback && showFeedback && (
            <div className={`feedback feedback--${scene.feedback.type}`} role="alert">
              {scene.feedback.text}
            </div>
          )}

          <div className="choices" role="group" aria-label="Choose your response">
            {scene.choices.map((choice, i) => (
              <button
                key={i}
                className="choice-button"
                onClick={() => handleChoice(choice)}
                aria-label={`Option ${i + 1}: ${choice.text}`}
              >
                {choice.text}
              </button>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
```

---

## Knowledge Checks

### Question Types

```json
{
  "questions": [
    {
      "type": "single-choice",
      "stem": "A colleague sends you a USB drive with project files. What should you do first?",
      "options": [
        { "text": "Plug it in — you trust your colleague", "correct": false },
        { "text": "Scan it with antivirus before opening any files", "correct": true },
        { "text": "Ask IT to check it", "correct": false, "partial": true },
        { "text": "Refuse to accept it", "correct": false }
      ],
      "feedback": {
        "correct": "Scanning removable media is standard protocol. Even trusted sources can unknowingly pass infected files.",
        "partial": "Asking IT is cautious but creates unnecessary delay. You can scan it yourself with standard tools.",
        "incorrect": "Never plug in unscanned media. USB drives are a common attack vector, even from trusted sources."
      },
      "difficulty": "intermediate",
      "objective": "identify-removable-media-risks",
      "bloom_level": "application"
    },
    {
      "type": "drag-drop-sort",
      "stem": "Order these incident response steps correctly:",
      "items": [
        { "text": "Contain the threat", "correct_position": 2 },
        { "text": "Identify the incident", "correct_position": 1 },
        { "text": "Eradicate the root cause", "correct_position": 3 },
        { "text": "Recover systems", "correct_position": 4 },
        { "text": "Document lessons learned", "correct_position": 5 }
      ],
      "feedback": {
        "correct": "The NIST framework follows: Identify → Contain → Eradicate → Recover → Lessons Learned.",
        "incorrect": "Review the NIST Incident Response lifecycle. Containment must happen before eradication."
      }
    },
    {
      "type": "hotspot",
      "stem": "Click on the three red flags in this email that indicate phishing:",
      "image": "media/phishing-email.png",
      "hotspots": [
        { "x": 120, "y": 45, "width": 200, "height": 20, "label": "Misspelled domain" },
        { "x": 50, "y": 180, "width": 300, "height": 30, "label": "Urgency language" },
        { "x": 200, "y": 320, "width": 150, "height": 20, "label": "Suspicious link URL" }
      ],
      "required_correct": 3
    },
    {
      "type": "confidence-rated",
      "stem": "What percentage of data breaches involve a human element?",
      "answer_type": "single-choice",
      "options": [
        { "text": "About 25%", "correct": false },
        { "text": "About 50%", "correct": false },
        { "text": "About 74%", "correct": true },
        { "text": "About 95%", "correct": false }
      ],
      "confidence_prompt": "How confident are you in your answer?",
      "confidence_levels": ["Guessing", "Somewhat confident", "Very confident"],
      "feedback": {
        "correct_high_confidence": "Exactly right, and you knew it. The 2023 Verizon DBIR found 74% of breaches involve the human element.",
        "correct_low_confidence": "You got it right! The Verizon DBIR puts it at 74%. Trust your instincts more.",
        "incorrect_high_confidence": "This is a common misconception worth correcting. The actual figure is 74% (Verizon DBIR 2023).",
        "incorrect_low_confidence": "Good that you flagged your uncertainty. The answer is 74% — the human element is the biggest factor."
      }
    }
  ]
}
```

### Quiz Engine Component

```tsx
// interactions/KnowledgeCheck.tsx
import { useState } from 'react';
import { motion } from 'framer-motion';

interface Question {
  type: string;
  stem: string;
  options?: Array<{ text: string; correct: boolean; partial?: boolean }>;
  feedback: Record<string, string>;
}

interface KnowledgeCheckProps {
  question: Question;
  onAnswer: (correct: boolean, score: number) => void;
}

export function KnowledgeCheck({ question, onAnswer }: KnowledgeCheckProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit() {
    if (selected === null) return;
    setSubmitted(true);

    const option = question.options![selected];
    const correct = option.correct;
    const partial = option.partial;
    const score = correct ? 1 : partial ? 0.5 : 0;

    onAnswer(correct, score);
  }

  const feedbackKey = submitted && selected !== null
    ? question.options![selected].correct ? 'correct'
      : question.options![selected].partial ? 'partial'
      : 'incorrect'
    : null;

  return (
    <div className="knowledge-check" role="group" aria-labelledby="question-stem">
      <p id="question-stem" className="question-stem">{question.stem}</p>

      <div className="options" role="radiogroup">
        {question.options?.map((option, i) => (
          <label
            key={i}
            className={`option ${submitted ? (option.correct ? 'correct' : selected === i ? 'incorrect' : '') : ''}`}
          >
            <input
              type="radio"
              name="answer"
              checked={selected === i}
              onChange={() => !submitted && setSelected(i)}
              disabled={submitted}
              aria-describedby={submitted ? 'feedback' : undefined}
            />
            <span>{option.text}</span>
          </label>
        ))}
      </div>

      {!submitted && (
        <button onClick={handleSubmit} disabled={selected === null}>
          Check Answer
        </button>
      )}

      {submitted && feedbackKey && (
        <motion.div
          id="feedback"
          className={`feedback feedback--${feedbackKey}`}
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          role="alert"
        >
          {question.feedback[feedbackKey]}
        </motion.div>
      )}
    </div>
  );
}
```

---

## Drag-and-Drop

### Accessible Implementation

Every drag-and-drop must have a keyboard alternative.

```tsx
// interactions/DragDropSort.tsx
import { useState, useCallback } from 'react';

interface SortItem {
  id: string;
  text: string;
  correctPosition: number;
}

interface DragDropSortProps {
  items: SortItem[];
  stem: string;
  onComplete: (correct: boolean) => void;
}

export function DragDropSort({ items: initialItems, stem, onComplete }: DragDropSortProps) {
  const [items, setItems] = useState(() =>
    [...initialItems].sort(() => Math.random() - 0.5)
  );
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);

  // Keyboard reordering
  const handleKeyDown = useCallback((e: React.KeyboardEvent, index: number) => {
    if (e.key === 'ArrowUp' && index > 0) {
      e.preventDefault();
      const newItems = [...items];
      [newItems[index], newItems[index - 1]] = [newItems[index - 1], newItems[index]];
      setItems(newItems);
      setFocusedIndex(index - 1);
    }
    if (e.key === 'ArrowDown' && index < items.length - 1) {
      e.preventDefault();
      const newItems = [...items];
      [newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]];
      setItems(newItems);
      setFocusedIndex(index + 1);
    }
  }, [items]);

  // Mouse drag
  const handleDragStart = (index: number) => setDraggedIndex(index);
  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;
    const newItems = [...items];
    const [dragged] = newItems.splice(draggedIndex, 1);
    newItems.splice(index, 0, dragged);
    setItems(newItems);
    setDraggedIndex(index);
  };
  const handleDragEnd = () => setDraggedIndex(null);

  function checkAnswer() {
    const correct = items.every((item, i) => item.correctPosition === i + 1);
    onComplete(correct);
  }

  return (
    <div className="drag-sort" role="region" aria-label={stem}>
      <p className="stem">{stem}</p>
      <p className="sr-only">Use arrow keys to reorder items, or drag with mouse.</p>
      <ol className="sortable-list" role="listbox" aria-label="Reorderable list">
        {items.map((item, i) => (
          <li
            key={item.id}
            role="option"
            tabIndex={0}
            draggable
            aria-grabbed={draggedIndex === i}
            aria-label={`${item.text}. Position ${i + 1} of ${items.length}. Use arrow keys to move.`}
            onDragStart={() => handleDragStart(i)}
            onDragOver={(e) => handleDragOver(e, i)}
            onDragEnd={handleDragEnd}
            onKeyDown={(e) => handleKeyDown(e, i)}
            onFocus={() => setFocusedIndex(i)}
            className={`sortable-item ${draggedIndex === i ? 'dragging' : ''}`}
            ref={el => { if (focusedIndex === i && el) el.focus(); }}
          >
            <span className="drag-handle" aria-hidden="true">⠿</span>
            {item.text}
          </li>
        ))}
      </ol>
      <button onClick={checkAnswer}>Check Order</button>
    </div>
  );
}
```

---

## Scroll-Driven Storytelling

### GSAP ScrollTrigger Setup

```tsx
// interactions/ScrollStory.tsx
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

interface StorySection {
  id: string;
  title: string;
  content: string;
  visual: string; // image or animation ID
  animation?: 'fade-up' | 'slide-left' | 'scale-in' | 'parallax';
}

interface ScrollStoryProps {
  sections: StorySection[];
}

export function ScrollStory({ sections }: ScrollStoryProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Respect reduced motion preference
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (prefersReduced) return;

      sections.forEach((section) => {
        const el = document.getElementById(`section-${section.id}`);
        if (!el) return;

        gsap.fromTo(el, {
          opacity: 0,
          y: section.animation === 'fade-up' ? 60 : 0,
          x: section.animation === 'slide-left' ? 100 : 0,
          scale: section.animation === 'scale-in' ? 0.8 : 1,
        }, {
          opacity: 1, y: 0, x: 0, scale: 1,
          duration: 0.8,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 80%',
            end: 'top 20%',
            toggleActions: 'play none none reverse',
          },
        });
      });

      // Progress indicator
      ScrollTrigger.create({
        trigger: containerRef.current,
        start: 'top top',
        end: 'bottom bottom',
        onUpdate: (self) => {
          const progressBar = document.getElementById('scroll-progress');
          if (progressBar) {
            progressBar.style.width = `${self.progress * 100}%`;
          }
        },
      });
    }, containerRef);

    return () => ctx.revert();
  }, [sections]);

  return (
    <div ref={containerRef} className="scroll-story">
      <div id="scroll-progress" className="progress-bar" role="progressbar" />
      {sections.map((section) => (
        <section key={section.id} id={`section-${section.id}`} className="story-section">
          <div className="section-content">
            <h2>{section.title}</h2>
            <p>{section.content}</p>
          </div>
          <div className="section-visual">
            <img src={section.visual} alt="" role="presentation" />
          </div>
        </section>
      ))}
    </div>
  );
}
```

---

## Interactive Video

### Video with Synchronized Content Panels

```tsx
// interactions/InteractiveVideo.tsx
import { useState, useRef, useEffect } from 'react';

interface VideoEvent {
  time: number;        // seconds
  type: 'panel-update' | 'quiz' | 'hotspot' | 'chapter';
  data: Record<string, unknown>;
}

interface InteractiveVideoProps {
  src: string;
  events: VideoEvent[];
}

export function InteractiveVideo({ src, events }: InteractiveVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeEvent, setActiveEvent] = useState<VideoEvent | null>(null);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      const t = video.currentTime;
      setCurrentTime(t);

      // Find active event
      const event = events.find(e =>
        Math.abs(e.time - t) < 0.5 && e !== activeEvent
      );

      if (event) {
        if (event.type === 'quiz') {
          video.pause();
          setPaused(true);
        }
        setActiveEvent(event);
      }
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    return () => video.removeEventListener('timeupdate', handleTimeUpdate);
  }, [events, activeEvent]);

  function resumeVideo() {
    videoRef.current?.play();
    setPaused(false);
    setActiveEvent(null);
  }

  return (
    <div className="interactive-video">
      <div className="video-container">
        <video ref={videoRef} src={src} controls>
          <track kind="captions" src={`${src.replace('.mp4', '.vtt')}`} label="English" default />
        </video>
      </div>

      {/* Side panel updates based on video position */}
      {activeEvent?.type === 'panel-update' && (
        <aside className="content-panel" aria-live="polite">
          <h3>{(activeEvent.data as any).title}</h3>
          <p>{(activeEvent.data as any).content}</p>
        </aside>
      )}

      {/* In-video quiz overlay */}
      {activeEvent?.type === 'quiz' && paused && (
        <VideoQuizOverlay
          question={(activeEvent.data as any).question}
          options={(activeEvent.data as any).options}
          onAnswer={(selectedIndex: number) => {
            const opt = (activeEvent.data as any).options[selectedIndex];
            // Track the answer, show feedback, then resume
            onQuizAnswer?.(activeEvent, selectedIndex, opt.correct);
            // Brief delay to show feedback before resuming
            setTimeout(resumeVideo, 2000);
          }}
        />
      )}

      {/* Chapter markers */}
      <div className="chapter-markers">
        {events.filter(e => e.type === 'chapter').map((chapter, i) => (
          <button
            key={i}
            className="chapter-marker"
            onClick={() => { if (videoRef.current) videoRef.current.currentTime = chapter.time; }}
            style={{ left: `${(chapter.time / (videoRef.current?.duration || 1)) * 100}%` }}
          >
            {(chapter.data as any).title}
          </button>
        ))}
      </div>
    </div>
  );
}
```

---

## Gamification Elements

### Progress and Achievement System

```typescript
// engine/gamification.ts
interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  condition: (state: CourseState) => boolean;
}

interface CourseState {
  modulesCompleted: string[];
  totalScore: number;
  perfectScores: number;
  streakDays: number;
  scenarioChoices: Record<string, string>;
  timeSpent: number;
}

const achievements: Achievement[] = [
  {
    id: 'first-module',
    title: 'Getting Started',
    description: 'Complete your first module',
    icon: '🎯',
    condition: (state) => state.modulesCompleted.length >= 1,
  },
  {
    id: 'perfect-score',
    title: 'Sharp Eye',
    description: 'Score 100% on a knowledge check',
    icon: '⭐',
    condition: (state) => state.perfectScores >= 1,
  },
  {
    id: 'security-hero',
    title: 'Security Hero',
    description: 'Make the right choice in every scenario',
    icon: '🛡️',
    condition: (state) => {
      const choices = Object.values(state.scenarioChoices);
      return choices.length >= 5 && choices.every(c => c === 'optimal');
    },
  },
];

export function checkAchievements(state: CourseState): Achievement[] {
  return achievements.filter(a => a.condition(state));
}

// Skill tree / progress map
interface SkillNode {
  id: string;
  title: string;
  prerequisiteIds: string[];
  moduleId: string;
  mastery: number; // 0-1
}

export function buildSkillTree(nodes: SkillNode[]): SkillNode[] {
  return nodes.map(node => ({
    ...node,
    unlocked: node.prerequisiteIds.every(
      preId => nodes.find(n => n.id === preId)?.mastery >= 0.7
    ),
  }));
}
```

---

## Spaced Repetition Integration

### Post-Course Review Schedule

```typescript
// engine/spaced-repetition.ts

interface ReviewItem {
  questionId: string;
  nextReviewDate: Date;
  interval: number;       // days
  easeFactor: number;     // SM-2 algorithm
  repetitions: number;
}

// SM-2 algorithm (SuperMemo)
export function calculateNextReview(
  item: ReviewItem,
  quality: number // 0-5 (0 = blackout, 5 = perfect)
): ReviewItem {
  let { interval, easeFactor, repetitions } = item;

  if (quality >= 3) {
    // Correct response
    if (repetitions === 0) interval = 1;
    else if (repetitions === 1) interval = 6;
    else interval = Math.round(interval * easeFactor);
    repetitions++;
  } else {
    // Incorrect — reset
    repetitions = 0;
    interval = 1;
  }

  easeFactor = Math.max(1.3,
    easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
  );

  const nextReviewDate = new Date();
  nextReviewDate.setDate(nextReviewDate.getDate() + interval);

  return { ...item, interval, easeFactor, repetitions, nextReviewDate };
}
```
