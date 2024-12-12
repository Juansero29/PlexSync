import dotenv from "dotenv";
dotenv.config();

import { SensCritiqueGqlClient } from "senscritique-graphql-api";
import { gql } from 'graphql-request';

console.log(`Using SensCritique account: ${process.env.SC_EMAIL}`);

type Product = {
  id: number;
  title: string;
  year_of_production: number;
  userInfos?: {
    isWished: boolean;
    isDone?: boolean;
    isListed?: boolean;
  };
};

async function getSensCritiqueWishlist() {
  const client = await SensCritiqueGqlClient.build(process.env.SC_EMAIL!, process.env.SC_PASSWORD!);

  const query = gql`
  query {
    myWishes {
      id
      title
      year_of_production
      userInfos {
        isWished
        isDone
        isListed
      }
    }
  }
`;


  const data: { myWishes: Product[] } = await client.request(query);

  console.log("Full API Response from SensCritique:", JSON.stringify(data, null, 2));

  const activeWishes = data.myWishes.filter((product) => product.userInfos?.isWished);
  console.log("Active Wishlist from SensCritique:", activeWishes);
}

getSensCritiqueWishlist();
