/**
 * Asset manifest. Paths are served from public/, so they are absolute URLs.
 * Only supplied assets are used — nothing is fetched externally.
 */

const A = '/assets';

export const ASSETS = {
  logo: `${A}/logos/elesoc_logo.png`,

  robotics: {
    buildCloseup: `${A}/robotics/robotics_build_closeup.png`,
    handsOn: `${A}/robotics/robotics_hands_on.png`,
    workspace: `${A}/robotics/robotics_workspace.png`,
  },

  makerlabs: {
    group: `${A}/makerlabs/makerlabs_group.jpeg`,
    soldering01: `${A}/makerlabs/soldering_workshop_01.png`,
    soldering02: `${A}/makerlabs/soldering_workshop_02.png`,
    printFarm: `${A}/makerlabs/print_farm.png`,
  },

  makerthon: {
    crowdWide: `${A}/makerthon/makerthon_crowd_wide.jpeg`,
    room: `${A}/makerthon/makerthon_room.jpeg`,
    teamWorking: `${A}/makerthon/makerthon_team_working.jpeg`,
    prizesTable: `${A}/makerthon/makerthon_prizes_table.jpeg`,
    winners: `${A}/makerthon/makerthon_winners.jpeg`,
    mentorshipRoom: `${A}/makerthon/makerthon_mentorship_room.jpeg`,
  },

  roboexpo: {
    heroCrowd: `${A}/roboexpo/roboexpo_hero_crowd.jpeg`,
    crowdWide: `${A}/roboexpo/roboexpo_crowd_wide.png`,
    officersGroup: `${A}/roboexpo/roboexpo_officers_group.png`,
    robotTrack: `${A}/roboexpo/roboexpo_robot_track.png`,
    analogueDrumDemo: `${A}/roboexpo/roboexpo_analogue_drum_demo.png`,
    sandMachineDemo: `${A}/roboexpo/roboexpo_sand_machine_demo.jpeg`,
    jarvisDemo: `${A}/roboexpo/roboexpo_jarvis_demo.jpeg`,
    demoersRoom: `${A}/roboexpo/roboexpo_demoers_room.jpeg`,
    teamsRoom: `${A}/roboexpo/roboexpo_teams_room.jpeg`,
  },

  cards: {
    makerthonHero: `${A}/designed_cards/makerthon_hero.png`,
    makerthonStats: `${A}/designed_cards/makerthon_stats.png`,
    roboexpoHero: `${A}/designed_cards/roboexpo_hero.png`,
    roboexpoStats: `${A}/designed_cards/roboexpo_stats.png`,
    roboexpoYearOfWork: `${A}/designed_cards/roboexpo_year_of_work.png`,
    roboexpoDemoers: `${A}/designed_cards/roboexpo_demoers.png`,
    roboexpoTeams: `${A}/designed_cards/roboexpo_teams.png`,
  },

  /** Clean cut-out project shots for the four-object hero sequence. */
  projects: {
    spider: `${A}/robotics/robot_spider.png`,
    drum: `${A}/robotics/analogue_drum_machine.png`,
    sand: `${A}/robotics/sand_machine_cad_01.png`,
    sandAlt: `${A}/robotics/sand_machine_cad_02.png`,
    jarvis: `${A}/robotics/desktop_jarvis.png`,
  },
};

/** Flat list of every image URL, for the preloader. */
export function allImageUrls() {
  const out = [];
  const walk = (node) => {
    if (typeof node === 'string') out.push(node);
    else if (node && typeof node === 'object') Object.values(node).forEach(walk);
  };
  walk(ASSETS);
  return [...new Set(out)];
}
