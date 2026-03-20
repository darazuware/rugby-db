export const prerender = true;
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  try {
    const allPlayers = await getCollection('players');
    const data = allPlayers.map(p => ({
      slug: p.slug,
      data: p.data
    }));

    return new Response(
      JSON.stringify(data),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ status: "error", message: "Failed to fetch player data" }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
