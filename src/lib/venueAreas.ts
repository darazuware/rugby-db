// src/lib/venueAreas.ts
// P4-2: 会場名 → 宿泊検索用エリアの対応表ルックアップ。
// 参照: docs/renewal/07_AFFILIATE.md, data/manual/venue_areas.json
//
// data/manual/venue_areas.json は手動管理のマッピングファイル（data/master/ ではない）。
// 未登録の会場（海外会場・未定など）は null を返し、呼び出し側は宿泊導線を非表示にする。
import venueAreasRaw from "../../data/manual/venue_areas.json";

export interface VenueArea {
    area: string;
    pref: string;
}

const VENUE_AREAS: Record<string, VenueArea> = Object.fromEntries(
    Object.entries(venueAreasRaw as Record<string, unknown>).filter(
        ([key]) => key !== "_comment"
    )
) as Record<string, VenueArea>;

/**
 * 会場名（home_ground / venue_raw）からエリア情報を引く。
 * 完全一致のみ（表記ゆれは venue_areas.json 側でキーを追加して対応する）。
 */
export function getVenueArea(venueName?: string | null): VenueArea | null {
    if (!venueName) return null;
    return VENUE_AREAS[venueName.trim()] ?? null;
}
