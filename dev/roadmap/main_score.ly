% main_score.ly
% ---------------------------------------------------------------------
% LilyPond score for a groovebox + TR-808 inspired track.
% Mirrors MML patterns: drums, 303-style bass, 80s lead, pads, and SFX.
% Intended as a seed for Copilot to extend with more sections and parts.

\version "2.24.0"

\header {
  title = "Open-Source Groovebox 808 Demo"
  subtitle = "MC-303 + TR-808 + 80s Synth + Retro Game SFX"
  composer = "Text-Based Music Toolchain"
}

global = {
  \key c \minor
  \time 4/4
  \tempo 4 = 125
}

% ---------------------------------------------------------------------
% DRUMS (TR-808 style)
% Map for open-source 808 kits:
%   bd = 808 kick
%   sn = 808 snare
%   hh = closed hat
%   hho = open hat
%   cp = clap
%   toml/tomm/tomh = 808 toms

drumPatternMain = \drummode {
  % 4 bars of basic 808 pattern (can be looped)
  % Bar 1
  bd4 hh8 hh8 sn4 hh8 hh8 |
  % Bar 2 (add clap on 2 + 4)
  bd4 hh8 hh8 sn4 cp4 |
  % Bar 3 (slight variation)
  bd4 hh8 hh8 sn8 hh8 bd8 hh8 |
  % Bar 4 (tom fill)
  bd4 toml8 tomm8 tomh8 tomm8 sn4 |
}

% Simple breakdown pattern
drumPatternBreak = \drummode {
  % Hats and sparse snares only
  hh8 hh hh hh hh hh hh hh |
  r4 sn4 r4 sn4 |
}

% ---------------------------------------------------------------------
% 303 / MC-303 style bassline (for FM or analogue synths)
% Suggest mapping this to a 303-ish synth (saw / square, high resonance)

bassLineA = \relative c {
  \global
  \clef bass

  % 4-bar acid-ish riff in C minor
  c8 c16 c16 g'8 f8 ees8 d8 |
  c8 r16 c16 g'8 f8 ees8 d8 |
  c8 c16 c16 bes8 g8 f8 ees8 |
  c8 r16 c16 g'8 f8 ees8 d8 |
}

% ---------------------------------------------------------------------
% 80s LEAD SYNTH (Juno / DX-style)
leadLineA = \relative c'' {
  \global
  \clef treble

  % Simple hook – syncopated 80s-style motif
  g8 g16 g16 f8 ees8 d4 r8 d8 |
  g8 g16 g16 bes8 g8 f4 r8 f8 |
  ees8 d16 c16 d8 ees8 f4 r8 f8 |
  g8 f16 ees16 d8 c8 d2 |
}

% ---------------------------------------------------------------------
% PADS (sustained 80s analogue-style chords)
padsA = \relative c' {
  \global
  \clef treble

  % Long, lush chords to sit under the groove
  <c ees g>1 |
  <bes d f>1 |
  <aes c ees>1 |
  <g bes d>1 |
}

% ---------------------------------------------------------------------
% RETRO GAME / FUNNY SFX (cue staff, notated as rough pitches)
% These can be mapped to:
%   - short square waves (game "bleeps")
%   - CC0 / open-source SFX (coin, jump, pop, power-up)

sfxLine = \relative c'' {
  \global

  % Bar 1: "coin" pickups (3 short bleeps)
  c16 c c r8 r4 r8 g16 g |
  % Bar 2: "power-up" rising arpeggio
  c16 e g c e g c8 r4 |
  % Bar 3: "cartoon pop" (downward sweep)
  g16 f ees d c bes aes g r4 |
  % Bar 4: silence (space for drums / bass to shine)
  r1 |
}

% ---------------------------------------------------------------------
% SCORE LAYOUT

\score {
  <<
    \new DrumStaff = "drums" <<
      \set DrumStaff.instrumentName = #"808 Kit"
      \drumPatternMain
      % TODO (Copilot): insert drumPatternBreak before final chorus, etc.
    >>

    \new Staff = "bass" <<
      \set Staff.instrumentName = #"303 Bass"
      \bassLineA
    >>

    \new Staff = "lead" <<
      \set Staff.instrumentName = #"80s Lead Synth"
      \leadLineA
    >>

    \new Staff = "pads" <<
      \set Staff.instrumentName = #"Analogue Pad"
      \padsA
    >>

    \new Staff = "sfx" <<
      \set Staff.instrumentName = #"Game / Nostalgic SFX"
      \sfxLine
    >>
  >>

  \layout { }
  \midi { }
}

% ---------------------------------------------------------------------
% TODO / HINTS FOR COPILOT
% - Add sections: Intro, Verse, Chorus, Break, Outro using \mark or
%   rehearsal marks.
% - Duplicate and vary bassLineA and leadLineA for B-sections.
% - Align drumPatternMain / drumPatternBreak more tightly with the MML
%   patterns in patterns/drums_808.mml.
% - Add more SFX cues for "open-source game" and "funny nostalgic" hits.
