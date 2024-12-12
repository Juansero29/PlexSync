import dotenv from "dotenv";
dotenv.config();

import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from 'graphql-request';

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);

// Define the type for a Product based on the GraphQL schema
type Product = {
  id: number;
  title: string;
  year_of_production: number;
  userInfos?: {
    isWished: boolean;
  };
};

async function getSensCritiqueWishlist() {
  // Build the SensCritique client
  const client = await SensCritiqueGqlClient.build(process.env.SC_EMAIL!, process.env.SC_PASSWORD!);

  // Define the GraphQL query with userInfos.isWished
  const query = gql`
    query {
      myWishes {
        id
        title
        year_of_production
        userInfos {
          isWished
        }
      }
    }
  `;

  // Fetch data from the API and cast the response to the appropriate type
  const data: { myWishes: Product[] } = await client.request(query);

  // Filter results to include only items with isWished === true
  const activeWishes = data.myWishes.filter((product) => product.userInfos?.isWished);

  // Output the filtered wishlist
  console.log("Active Wishlist from SensCritique:", activeWishes);
}

// Execute the function
getSensCritiqueWishlist();
