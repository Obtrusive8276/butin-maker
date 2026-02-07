export interface FileItem {
  path: string;
  name: string;
  is_dir: boolean;
  size: number;
  extension: string;
}

export interface DirectoryListing {
  current_path: string;
  parent_path: string | null;
  items: FileItem[];
}

export interface QBittorrentSettings {
  host: string;
  port: number;
  username: string;
  password: string;
}

export interface TrackerSettings {
  announce_url: string;
  upload_url: string;
  lacale_api_key: string;
}

export interface PathSettings {
  default_browse_path: string;
  hardlink_path: string;
  qbittorrent_download_path: string;
  output_path: string;
}

export interface TMDBSettings {
  api_key: string;
}

export interface Settings {
  qbittorrent: QBittorrentSettings;
  tracker: TrackerSettings;
  paths: PathSettings;
  tmdb: TMDBSettings;
}

export interface TorrentCreateRequest {
  source_path: string;
  name?: string;
  piece_size?: number;
  private?: boolean;
  tracker_url?: string;
}

export interface TorrentResponse {
  success: boolean;
  torrent_path?: string;
  torrent_name?: string;
  info_hash?: string;
  size?: number;
  piece_count?: number;
  error?: string;
}

export interface VideoTrack {
  codec: string | null;
  width: number | null;
  height: number | null;
  bitrate: number | null;
  framerate: number | null;
  duration: number | null;
  hdr: string | null;
}

export interface AudioTrack {
  codec: string | null;
  channels: number | null;
  bitrate: number | null;
  language: string | null;
  title: string | null;
}

export interface SubtitleTrack {
  codec: string | null;
  language: string | null;
  title: string | null;
  forced: boolean;
}

export interface MediaInfo {
  file_path: string;
  file_name: string;
  file_size: number;
  container: string | null;
  duration: number | null;
  video_tracks: VideoTrack[];
  audio_tracks: AudioTrack[];
  subtitle_tracks: SubtitleTrack[];
}

export interface PresentationData {
  poster_url: string;
  title: string;
  rating: string;
  genre: string;
  synopsis: string;
  quality: string;
  format: string;
  video_codec: string;
  audio_codec: string;
  languages: string;
  subtitles: string;
  size: string;
}

export type Step = 'files' | 'tmdb' | 'nfo' | 'rename' | 'torrent' | 'finalize';

// La Cale API types
export interface LaCaleTag {
  id: string;
  name: string;
  slug: string;
}

export interface LaCaleTagGroup {
  id: string;
  name: string;
  slug: string;
  order?: number;
  tags: LaCaleTag[];
}

export interface LaCaleCategory {
  id: string;
  name: string;
  slug: string;
  icon?: string;
  parentId?: string;
  children: LaCaleCategory[];
}

export interface LaCaleMetaResponse {
  categories: LaCaleCategory[];
  tagGroups: LaCaleTagGroup[];
  ungroupedTags: LaCaleTag[];
}

export interface LaCaleUploadRequest {
  title: string;
  category_id: string;
  torrent_file_path: string;
  tag_ids?: string[];
  description?: string;
  tmdb_id?: string;
  tmdb_type?: string;
  cover_url?: string;
  nfo_file_path?: string;
}

export interface LaCaleUploadResponse {
  success: boolean;
  id?: string;
  slug?: string;
  link?: string;
  error?: string;
}
