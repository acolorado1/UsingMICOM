from micom.qiime_formats import load_qiime_medium
import pandas as pd 
import argparse as arg 

parser = arg.ArgumentParser(description="Takes qza files of mediums and interpolates a combined diet")
parser.add_argument("-m1", type=str, help="file path for qza formatted file",
                    default="/data/diets/data/diets/western_diet_gut.qza")
parser.add_argument("-m2", type=str, help="file path for qza formatted file",
                    default = "data/diets/vmh_high_fiber_agora.qza")
parser.add_argument("-n", type=float, help="interpolation factor between 0 and 1", 
                    default=0.5)
parser.add_argument("-o", type=str, help="file path for output file", 
                    default="folder/filename.csv")
args = parser.parse_args()

# this function is not necessary, but allows us to derive a medium with metabolites/concentrations 
# between two diets (e.g. intermediate of Western Diet and High Fiber Diet)
def interpolate_fluxes(medium_1, medium_2, n, output_path):
    """
    Interpolates fluxes between two chemical environments.
    
    Parameters:
    medium_1 (qza): qza containing the fluxes for the medium_1.
    medium_2 (qza): qza containing the fluxes for the medium_2.
    n (float): Interpolation factor, fraction of medium_1 (0 <= n <= 1) 
              (e.g. 1 is only medium_1, 0 is only medium_2, 0.5 is halfway between medium_1 and medium_2)
    
    Returns:
    pd.Series: Interpolated fluxes.
    """

    if not (0 <= n <= 1):
        raise ValueError("n must be between 0 and 1")
    
    # convert qza to pandas df 
    medium_1 = load_qiime_medium(medium_1)
    medium_2 = load_qiime_medium(medium_2)
    
    # Extract the flux series from the dataframes
    medium_1_series = medium_1['flux']
    medium_2_series = medium_2['flux']
    
    # Combine the indices of both series and remove duplicates
    all_rxns = list(set(medium_1_series.index).union(set(medium_2_series.index)))
    
    # Ensure indices are unique and create DataFrame with both series
    medium_1_series = medium_1_series[~medium_1_series.index.duplicated(keep='first')]
    medium_2_series = medium_2_series[~medium_2_series.index.duplicated(keep='first')]
    
    combined_df = pd.DataFrame(index=all_rxns)
    combined_df['medium_1_flux'] = medium_1_series.reindex(combined_df.index)
    combined_df['medium_2_flux'] = medium_2_series.reindex(combined_df.index)
    
    # Fill NaN values with 0 (assuming missing flux is 0)
    combined_df = combined_df.fillna(0)
    
    # Linearly interpolate the fluxes
    interpolated_flux = (1 - n) * combined_df['medium_1_flux'] + n * combined_df['medium_2_flux']
    interpolated_flux.to_csv(output_path)

    # change column names
    df = pd.read_csv(output_path)
    df.columns = ['reaction', 'flux']
    df.to_csv(output_path)
    return None

interpolate_fluxes(args.m1, args.m2, args.n, args.o)