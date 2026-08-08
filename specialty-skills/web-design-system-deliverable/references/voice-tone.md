# Voice and Tone

Define how the brand speaks across every piece of UI text. Voice is constant. Tone shifts by context.

## 1. Voice Attributes

Define 3-4 core voice attributes. Each attribute has a boundary to prevent overcorrection.

### Attribute Template

```
Attribute: [quality] but not [excess]
Description: [One sentence explaining what this means in practice]
Example: "Your changes are saved." — [why this demonstrates the attribute]
Anti-pattern: "Your changes have been successfully saved to our servers!" — [why this violates it]
```

### Example Set

```
Attribute: Confident but not arrogant
Description: State things directly. Don't hedge, don't boast.
Example: "Your account is ready."
Anti-pattern: "Congratulations! You've successfully created your amazing new account!"

Attribute: Precise but not cold
Description: Give people exactly the information they need. Stay human.
Example: "2 items removed from your cart."
Anti-pattern: "Item removal operation completed for 2 objects."

Attribute: Warm but not performative
Description: Be genuinely helpful without forced enthusiasm.
Example: "Need help? We're here."
Anti-pattern: "We'd LOVE to help you! Don't hesitate to reach out!!!"

Attribute: Clear but not simplistic
Description: Respect the reader's intelligence while removing ambiguity.
Example: "This action can't be undone."
Anti-pattern: "Warning: Proceeding will initiate an irreversible action sequence."
```

Define 3-4 attributes for the brand. Use the same format. Derive attributes from the brand personality spectrum in the strategy phase.

## 2. Messaging Hierarchy

Tone shifts as the message gets longer and more detailed.

| Level | Purpose | Tone | Length | Example |
|---|---|---|---|---|
| Tagline | Brand identity in a phrase | Distilled, evocative | 2-8 words | "Think different" |
| Headline | Lead a page or section | Confident, clear | 3-12 words | "One workspace for your whole team" |
| Subhead | Support the headline | Informative, specific | 8-20 words | "Bring projects, docs, and team chat together in one place" |
| Body | Explain or persuade | Conversational, helpful | 1-3 sentences | Full description of a feature or benefit |
| Microcopy | Guide in-context action | Functional, brief | 1-8 words | "Drag to reorder" |
| Legal | Protect the business | Neutral, precise | As needed | Terms, disclaimers, compliance text |

Rules:

- Personality is strongest at the tagline and headline level.
- Personality fades as you move toward microcopy and legal.
- Microcopy should be invisible — users should act, not read.
- Never inject brand personality into legal or compliance text.

## 3. CTA Conventions

### Verb-First Pattern

Start CTAs with a verb. The verb tells the user what will happen.

| Urgency | Pattern | Example |
|---|---|---|
| High | Direct imperative | "Start free trial" |
| Medium | Action + benefit | "Get your report" |
| Low | Invitation | "Learn more" / "See how it works" |

### Rules

- Use imperative for primary actions: "Create account", "Save changes", "Send message".
- Use invitation for secondary/exploratory actions: "Learn more", "See pricing", "Explore features".
- Match the verb to the outcome, not the mechanism. "Get started" not "Submit form".
- Keep CTAs to 1-4 words. Five is the hard limit.
- Never use "Click here" or "Submit".
- Pair destructive actions with specificity: "Delete project" not "Delete".

### Do / Don't

```
Do:    "Save changes"
Don't: "Submit"

Do:    "Create account"
Don't: "Sign up now!!!"

Do:    "Remove from cart"
Don't: "Click here to remove"

Do:    "Start free trial"
Don't: "Get started with your free trial today"
```

## 4. Error and Empty State Copy

### Tone Rules for Failure States

- Be direct about what happened.
- Tell the user what to do next.
- Offer reassurance only when something was at risk (data loss, payment).
- Never blame the user.
- Never use "Oops" or fake-casual apologies for serious errors.

### Error Template

```
[What happened] + [What to do] + [Reassurance if needed]
```

Examples:

```
"Connection lost. Check your internet and try again."
"That email is already registered. Try signing in instead."
"Payment failed. Your card wasn't charged. Try a different payment method."
"Something went wrong. Try again, or contact support if it keeps happening."
```

### Empty State Template

```
[What belongs here] + [How to fill it]
```

Examples:

```
"No projects yet. Create your first project to get started."
"No results for '[query]'. Try a broader search term."
"No notifications. You're all caught up."
```

Rules:

- Empty states are onboarding opportunities. Use them to guide action.
- Error states must always include a recovery path.
- Keep error copy under 25 words.

## 5. Naming Principles

### Feature and Product Naming

| Approach | When to Use | Example |
|---|---|---|
| Concrete / descriptive | Core features, navigation, actions | "Dashboard", "Team settings", "Export" |
| Abstract / branded | Flagship features, tier names, campaigns | "Spark", "Pro", "Horizon" |
| Hybrid | Feature suites, branded tools | "Smart Compose", "Quick Share" |

Rules:

- Default to concrete. Use abstract only when the feature deserves brand equity.
- Abstract names require onboarding — budget the explanation cost.
- Tier names should imply progression: Free → Pro → Enterprise, not Gold → Diamond → Platinum.
- Never name a feature something the user has to Google to understand.
- Be consistent: if one feature uses verb-noun ("Quick Share"), related features should follow the same pattern.

### Brand Vocabulary

Maintain a short glossary of terms the brand uses consistently:

```
| Standard Term | We Say   | We Don't Say       |
|---------------|----------|--------------------|
| workspace     | space    | room, environment  |
| collaborator  | teammate | member, user       |
| upgrade       | upgrade  | upsell, purchase   |
```

Keep this list under 15 entries. More than that means the vocabulary isn't disciplined.

## 6. Content Rules Per Component

### Buttons

- Casing: sentence case
- Length: 1-4 words
- Punctuation: none
- Pattern: verb + noun when ambiguous ("Save draft"), verb alone when context is clear ("Save")
- Icon: leading position only, optional

### Badges / Tags

- Casing: sentence case
- Length: 1-2 words
- Punctuation: none
- Pattern: status or category label ("Active", "Beta", "Overdue")
- Avoid full sentences

### Alerts / Banners

- Casing: sentence case
- Length: 1-2 sentences
- Punctuation: periods for full sentences, none for fragments
- Pattern: [status/context] + [action if needed]
- Example: "Your trial ends in 3 days. Upgrade to keep your data."

### Tooltips

- Casing: sentence case
- Length: 1 sentence, under 80 characters
- Punctuation: period only if a full sentence
- Pattern: clarify what the element does, not what it is
- Example: "Filters results by date added"
- Do not repeat the label the tooltip is attached to

### Modals

- Title: sentence case, 2-6 words, state the action or question
- Body: 1-3 sentences max
- Primary action: matches the title verb ("Delete project" title → "Delete" button)
- Cancel: always "Cancel", not "Go back" or "Never mind"

### Form Labels

- Casing: sentence case
- Length: 1-3 words
- Punctuation: no colons, no periods
- Helper text: one sentence, explains format or constraint ("Must be at least 8 characters")
- Required indicator: asterisk (*) after the label, no word "required" unless accessibility demands it

### Placeholder Text

- Casing: sentence case
- Pattern: example value or brief instruction
- Example: "jane@example.com" or "Search by name or email"
- Never use placeholder as a substitute for a label

## Validation Checklist

Before shipping voice and tone guidance:

- Voice attributes are defined with boundaries and anti-patterns
- Messaging hierarchy covers all six levels
- CTA conventions include do/don't examples
- Error and empty state templates are documented
- Naming principles distinguish concrete from abstract
- Component-level content rules cover casing, length, and punctuation
- A brand vocabulary glossary exists, even if short
