export const TEAM_SLUG_MAP: Record<string, string> = {
    静岡ブルーレヴズ: "shizuoka-blue-revs",
    東京サントリーサンゴリアス: "tokyo-suntory-sungoliath",
    "浦安D-Rocks": "urayasu-d-rocks",
    コベルコ神戸スティーラーズ: "kobelco-kobe-steelers",
    埼玉パナソニックワイルドナイツ: "saitama-panasonic-wild-knights",
    東芝ブレイブルーパス東京: "toshiba-brave-lupus-tokyo",
    トヨタヴェルブリッツ: "toyota-verblitz",
    三重ホンダヒート: "mie-honda-heat",
    三菱重工相模原ダイナボアーズ: "mitsubishi-sagamihara-dynaboars",
    横浜キヤノンイーグルス: "yokohama-canon-eagles",
    リコーブラックラムズ東京: "ricoh-black-rams-tokyo",
    NECグリーンロケッツ東葛: "nec-green-rockets-tokatsu",
    九州電力キューデンヴォルテクス: "kyuden-voltex",
    清水建設江東ブルーシャークス: "shimizu-koto-blue-sharks",
    豊田自動織機シャトルズ愛知: "toyota-shuttles-aichi",
    日本製鉄釜石シーウェイブス: "kamaishi-seawaves",
    花園近鉄ライナーズ: "hanazono-kintetsu-liners",
    日野レッドドルフィンズ: "hino-red-dolphins",
    レッドハリケーンズ大阪: "hurricanes",
    クリタウォーターガッシュ昭島: "kurita-water-gush-akishima",
    狭山セコムラガッツ: "secom-rugguts",
    中国電力レッドレグリオンズ: "chugoku-red-regulions",
    マツダスカイアクティブズ広島: "mazda-skyactivs-hiroshima",
    ヤクルトレビンズ戸田: "yakult-levins",
    "クボタスピアーズ船橋・東京ベイ": "kubota-spears-funabashi-tokyo-bay",
    ルリーロ福岡: "leriro-fukuoka",
};

/**
 * チーム名からスラッグを取得する
 * @param name チーム名
 * @returns スラッグ
 */
export function getTeamSlug(name: string): string {
    if (TEAM_SLUG_MAP[name]) {
        return TEAM_SLUG_MAP[name];
    }
    // 特殊文字の置換と小文字化
    return name
        .toLowerCase()
        .replace(/\s+/g, "-")
        .replace(/[・.&\/]/g, "-")
        .replace(/-+/g, "-")
        .replace(/^-|-$/g, "");
}
