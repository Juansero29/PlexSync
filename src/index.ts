import dotenv from "dotenv";

import fetch from "node-fetch";
import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from "graphql-request";
import { XMLParser } from "fast-xml-parser";


type Media = {
  avatar: string;
  __typename: string;
};

type ProductMedia = {
  picture: string;
  __typename: string;
};

type Product = {
  id: number;
  genres: string[];
  medias: ProductMedia;
  year_of_production: number;
  release_date: string;
  title: string;
  myRating: number | null;
  myWish: boolean | null;
  targetWish: boolean | null;
  universe: string;
  __typename: string;
};

type User = {
  id: number;
  medias: Media;
  wishes: Product[];
  __typename: string;
};

type UserWishesResponse = {
  user: User;
};

type Me = {
  id: number;
  email: string;
  name: string;
  url: string;
};


dotenv.config();

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);


async function fetchPlexWatchlist(): Promise<void> {
  const token = process.env.PLEX_TOKEN!;
  const endpoint = `https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=${token}`;

  try {
    console.log("Fetching watchlist from Plex...");

    const response = await fetch(endpoint);
    if (!response.ok) {
      throw new Error(`Failed to fetch watchlist: ${response.statusText}`);
    }

    const xmlData = await response.text();

    // Configure the XML parser to parse attributes
    const parser = new XMLParser({
      ignoreAttributes: false, // Ensures attributes like `title` and `year` are preserved
      attributeNamePrefix: "", // Removes @ prefix from attribute keys
    });
    const jsonData = parser.parse(xmlData);

    const watchlist = jsonData.MediaContainer?.Video || [];
    if (watchlist.length === 0) {
      console.log("Your Plex watchlist is empty.");
    } else {
      console.log("\nPlex Watchlist:");
      watchlist.forEach((item: any) => {
        const title = item?.title || item?.title || "Unknown Title";
        const year = item?.year || item?.year || "Unknown Year";
        console.log(`- ${title} (${year})`);
      });
    }
  } catch (error) {
    console.error("Error fetching Plex watchlist:", error);
  }
}

// Fetch User Wishes from SensCritique
async function listUserWishes(): Promise<void> {
  const client = await SensCritiqueGqlClient.build(
    process.env.SC_EMAIL!,
    process.env.SC_PASSWORD!
  );

  const userWishesQuery = gql`
    query UserWishes(
      $avatarSize: String
      $id: Int!
      $universe: String
      $sortBy: String
      $limit: Int
      $offset: Int
      $pictureSize: String
    ) {
      user(id: $id) {
        id
        medias(avatarSize: $avatarSize) {
          avatar
          __typename
        }
        wishes(
          universe: $universe
          sortBy: $sortBy
          limit: $limit
          offset: $offset
        ) {
          id
          genres
          medias(pictureSize: $pictureSize) {
            picture
            __typename
          }
          year_of_production
          release_date
          title
          myRating
          myWish
          targetWish
          universe
          __typename
        }
        __typename
      }
    }
  `;

  const variables = {
    avatarSize: "30x30",
    id: 724296, // Replace with your actual user ID
    universe: "",
    sortBy: "user_last_action",
    limit: 30,
    offset: 0,
    pictureSize: "150",
  };

  try {
    const data = await client.request(userWishesQuery, variables);

    console.log(`User ID: ${data.user.id}`);
    console.log(`User Avatar: ${data.user.medias.avatar}`);
    console.log("Wishes:");
    data.user.wishes.forEach((wish: Product) => {
      console.log(`- ${wish.title} (${wish.year_of_production})`);
      console.log(`  Genres: ${wish.genres.join(", ")}`);
      console.log(`  Release Date: ${wish.release_date}`);
      console.log(`  Universe: ${wish.universe}`);
      console.log(`  Picture: ${wish.medias.picture}`);
    });
    
  } catch (error) {
    console.error("Error fetching user wishes:", error);
  }
}

/**
 * Fetch media by title and release year, and return the media ID.
 */
async function fetchMediaId(title: string, year: number, universe: string): Promise<number | null> {
  const client = await SensCritiqueGqlClient.build(
    process.env.SC_EMAIL!,
    process.env.SC_PASSWORD!
  );

  const searchMediaQuery = gql`
    query SearchMedia($keywords: String!, $universe: String) {
      searchResult(keywords: $keywords, universe: $universe, limit: 5) {
        results {
          products_list {
            id
            title
            year_of_production
          }
        }
      }
    }
  `;

  const variables = {
    keywords: title,
    universe: universe,
  };

  const data = await client.request(searchMediaQuery, variables);

  const results = data.searchResult.results[0].products_list;

  for (const result of results) {
    if (result.year_of_production === year) {
      console.log(`Found media: ${result.title} (${result.year_of_production})`);
      return result.id;
    }
  }

  console.log(`No media found for "${title}" (${year}).`);
  return null;
}

/**
 * Add media to SensCritique wishlist.
 */
async function addMediaToWishlist(title: string, year: number, universe: string): Promise<void> {
  const mediaId = await fetchMediaId(title, year, universe);
  
  if (!mediaId) {
    console.error("Media not found. Cannot add to wishlist.");
    return;
  }

  const client = await SensCritiqueGqlClient.build(
    process.env.SC_EMAIL!,
    process.env.SC_PASSWORD!
  );

  const addToWishlistMutation = gql`
    mutation AddToWishlist($productId: Int!) {
      productWish(productId: $productId)
    }
  `;

  try {
    const data = await client.request(addToWishlistMutation, { productId: mediaId });
    if (data.productWish) {
      console.log(`Successfully added media (ID: ${mediaId}) to the wishlist.`);
    } else {
      console.error("Failed to add media to wishlist.");
    }
  } catch (error) {
    console.error("Error adding media to wishlist:", error);
  }
}

// Example usage:
(async () => {
  const title = "Amadeus";
  const year = 1984;
  const universe = "movie"; // or "tvshow"
  // console.log("\nFetching SensCritique User Wishes...\n");
  // await listUserWishes();
  // console.log("Fetching Plex and SensCritique data...\n");
  // await fetchPlexWatchlist();
  await addMediaToWishlist(title, year, universe);
})();
