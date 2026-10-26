/**
 * Home workout plans for the website, made by Grasp's own planner.
 *
 * Each plan is one training week: the engine is asked for session 1, told it
 * happened, asked for session 2, and so on — exactly how the app builds a week
 * — for a fixed setup (equipment, days, level, goal) and a fixed seed, so the
 * same input always gives the same plan.
 *
 * Run from the app repo, so its packages resolve:
 *   cd C:/dev/fitbud-viral && npx vite-node C:/dev/grasp-site-pseo/build/plans/generate.ts
 * Writes build/plans/plans.json next to this file.
 */
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const APP = process.env.FITBUD ?? 'C:/dev/fitbud-viral';
const { generateWorkout } = await import(`${APP}/packages/fitness-engine/src/index.ts`);
const { SEED_CONTENT } = await import(`${APP}/packages/content/src/index.ts`);

type Setup = { key: string; equipment: string[] };

/** What people train with at home, smallest kit first. */
const SETUPS: Setup[] = [
  { key: 'bodyweight', equipment: [] },
  { key: 'dumbbells', equipment: ['dumbbell'] },
  { key: 'dumbbells-bench', equipment: ['dumbbell', 'adjustable_bench'] },
  { key: 'dumbbells-pullup-bar', equipment: ['dumbbell', 'pullup_bar'] },
  { key: 'resistance-bands', equipment: ['resistance_band'] },
  { key: 'kettlebell', equipment: ['kettlebell'] },
];
const DAYS = [3, 4, 5];
const LEVELS = ['beginner', 'intermediate'];
const GOALS = ['hypertrophy', 'fat_loss'];
const MINUTES = 45;
const SEED = 11;

// Training days spread through a week starting Monday 2 Nov 2026.
const DAY_OFFSETS: Record<number, number[]> = { 3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 4, 5] };

function week(setup: Setup, days: number, level: string, goal: string) {
  const recent: { split: string | null; completedAt: string; muscles: string[]; exerciseSlugs: string[] }[] = [];
  const sessions = [];
  for (const offset of DAY_OFFSETS[days]) {
    const date = new Date(Date.UTC(2026, 10, 2 + offset)).toISOString().slice(0, 10);
    const plan = generateWorkout({
      date,
      seed: SEED + offset,
      durationMinutes: MINUTES,
      user: { experienceLevel: level, goal, preferredSplit: 'auto', daysPerWeek: days, warmupSets: false },
      availableEquipment: setup.equipment,
      library: SEED_CONTENT.exercises,
      performance: [],
      preferences: [],
      recentSessions: [...recent],
    });
    sessions.push({
      date,
      split: plan.split,
      splitName: plan.splitName,
      minutes: plan.estimatedMinutes,
      warnings: plan.warnings,
      exercises: plan.exercises.map((e: any) => ({
        slug: e.exerciseSlug,
        role: e.role,
        sets: e.targetSets,
        repMin: e.targetRepMin,
        repMax: e.targetRepMax,
        seconds: e.durationSeconds,
        work: e.intervalWorkSeconds ?? null,
        workRest: e.intervalRestSeconds ?? null,
        rest: e.restSeconds,
      })),
    });
    const muscles = new Set<string>();
    for (const e of plan.exercises) {
      const ex = SEED_CONTENT.exercises.find((x: any) => x.slug === e.exerciseSlug);
      ex?.muscles.filter((m: any) => m.role === 'primary').forEach((m: any) => muscles.add(m.muscle));
    }
    recent.unshift({
      split: plan.split,
      completedAt: `${date}T18:00:00.000Z`,
      muscles: [...muscles],
      exerciseSlugs: plan.exercises.map((e: any) => e.exerciseSlug),
    });
  }
  return sessions;
}

const plans = [];
for (const setup of SETUPS)
  for (const days of DAYS)
    for (const level of LEVELS)
      for (const goal of GOALS)
        plans.push({ setup: setup.key, equipment: setup.equipment, days, level, goal, minutes: MINUTES,
                     sessions: week(setup, days, level, goal) });

const out = join(dirname(fileURLToPath(import.meta.url)), 'plans.json');
writeFileSync(out, JSON.stringify(plans, null, 1));
console.log(`${plans.length} plans -> ${out}`);
