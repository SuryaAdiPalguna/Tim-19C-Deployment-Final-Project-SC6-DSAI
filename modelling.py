import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds

def main(df, pilihan_kategori, pilihan_supermarket):
    df_categorized = (df.loc[df["kategori"] == pilihan_kategori])

    """### Proses"""

    average_harga_produk_per_unit_pivot_df = (df_categorized.reset_index().pivot_table(index="nama_toko", columns="nama", values="average_harga_produk_per_unit").fillna(0))

    R = average_harga_produk_per_unit_pivot_df.values
    supermarket_average_harga_produk_per_unit_mean = np.mean(R, axis=1)
    R_demeaned = R - supermarket_average_harga_produk_per_unit_mean.reshape(-1, 1)

    U, sigma, Vt = svds(R_demeaned, k=average_harga_produk_per_unit_pivot_df.shape[0]-1)
    sigma = np.diag(sigma)

    predictions = U @ sigma @ Vt

    all_supermarket_predicted_products = np.dot(np.dot(U, sigma), Vt) + supermarket_average_harga_produk_per_unit_mean.reshape(-1, 1)
    
    preds_df = pd.DataFrame(all_supermarket_predicted_products, columns=average_harga_produk_per_unit_pivot_df.columns)

    # credit: https://www.kaggle.com/code/abhisek11/book-recommendation-using-matrix-factorization ---
    def recommend_products(predictions_df, pilihan_supermarket, original_df, num_recommendations=5):
        supermarket_row_number = list(df_categorized["nama_toko"].unique()).index(pilihan_supermarket)
        sorted_supermarket_predictions = predictions_df.loc[supermarket_row_number].sort_values(ascending=False)

        supermarket_data_full = original_df[original_df["nama_toko"] == (pilihan_supermarket)]
        recommendations = supermarket_data_full.merge(pd.DataFrame(sorted_supermarket_predictions).reset_index(), how='left', left_on='nama', right_on = 'nama').sort_values('average_harga_produk_per_unit', ascending=True).iloc[:num_recommendations, :-1]

        return(supermarket_data_full, recommendations)

    """### Output"""

    already_rated, predictions = recommend_products(preds_df, pilihan_supermarket, df_categorized, 8)
    return already_rated, predictions
