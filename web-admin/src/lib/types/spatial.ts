type AnchorRow = {
  anchor_id: string;
  kind: string;
  title: string;
  status: string;
  config_json: string;
  created_at: number;
  updated_at: number;
};

type PlaceRow = {
  place_id: string;
  anchor_id: string;
  space: string;
  loc_id: string;
  depth: number | null;
  instance: string | null;
  label: string | null;
  created_at: number;
  updated_at: number;
};

type FileTagRow = {
  file_path: string;
  place_id: string;
  source: string;
  created_at: number;
  anchor_id: string;
  space: string;
  loc_id: string;
};

export type { AnchorRow, PlaceRow, FileTagRow };
