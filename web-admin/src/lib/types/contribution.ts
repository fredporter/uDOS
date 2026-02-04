export interface ContributionManifest {
  id: string;
  status: string;
  mission_id?: string;
  artifact?: string;
  notes?: string;
  status_history?: { status: string; reviewer?: string | null; note?: string | null; ts: string }[];
}

export interface ContributionRow {
  id: string;
  status: string;
  path: string;
  manifest: ContributionManifest;
}
