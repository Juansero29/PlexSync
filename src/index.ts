import dotenv from "dotenv";
dotenv.config();

import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from 'graphql-request';

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);

type UserInfos = {
  isWished: boolean;
  isDone?: boolean;
  isListed?: boolean;
};

type Product = {
  id: number;
  title: string;
  year_of_production: number;
  original_title?: string;
  rating?: number;
  release_date?: string;
  universe?: string;
  date_done?: string;
  myRating?: number;
  myWish?: boolean;
  targetRating?: number;
  targetWish?: boolean;
  userInfos?: UserInfos;
};

async function getSensCritiqueWishlist(): Promise<void> {
  const client = await SensCritiqueGqlClient.build(process.env.SC_EMAIL!, process.env.SC_PASSWORD!);

  const query = gql`
    query {
      myWishes {
        id
        title
        year_of_production
        original_title
        rating
        release_date
        universe
        year_of_production
        date_done
        myRating
        myWish
        targetRating
        targetWish
        userInfos {
          isWished
          isDone
          isListed
        }
      }
    }
  `;

  try {
    const data: { myWishes: Product[] } = await client.request(query);

    const currentTime = new Date().toLocaleString();
    const simplifiedResponse = data.myWishes.map((product) => ({
      title: product.title,
      original_title: product.original_title,
      release_date: product.release_date,
    }));
    console.log(`[${currentTime}] Simplified API Response:`, simplifiedResponse);

    const activeWishes = data.myWishes.filter((product) => product.userInfos?.isWished);
    console.log(`[${currentTime}] Active Wishlist from SensCritique:`, activeWishes);

    if (activeWishes.length === 0) {
      console.log(`[${currentTime}] No active wishes found. Retrying in 30 seconds...`);
      setTimeout(() => getSensCritiqueWishlist(), 30000);
    } else {
      console.log(`[${currentTime}] Active wishes found. Stopping retries.`);
    }
  } catch (error) {
    const currentTime = new Date().toLocaleString();
    console.error(`[${currentTime}] Error fetching wishlist:`, error);
    console.log(`[${currentTime}] Retrying in 30 seconds...`);
    setTimeout(() => getSensCritiqueWishlist(), 30000);
  }
}

getSensCritiqueWishlist();
