#include <iostream>
#include <fstream>
#include <map>


void usage(){
	std::cout << "\nUsage: " << "similaritems [-k shingle-size] [-t sim-threshold] [-path path]" << "\n" << std::endl;
	std::cout << "\t-k:\tShingle size. Defaults to 9" << std::endl;
	std::cout << "\t-t:\tSimilarity threshold. Defaults to .8" << std::endl;
	std::cout << "\t-path:\tPath file files, or single file. No default value" << std::endl;
	std::cout << "\n" << std::endl;
}

void parseParams(int argc, char** argv, int &k, float &threshold, std::string &path){

	if (argc < 2){
		usage(), exit(1);
	}

	int i = 0;
	k = -1;
	threshold = -1;

	while (i < argc){
		if (std::strcmp(argv[i], "-k") == 0 || std::strcmp(argv[i], "--k") == 0){
			if (i+1 >= argc){
				std::cout << "Missing value for [k]" << std::endl;
				usage(), exit(1);
			}

			k = std::stoi(argv[i+1]);
			i++;
		} else if (std::strcmp(argv[i], "-t") == 0 || std::strcmp(argv[i], "--t") == 0){
			if (i+1 >= argc){
				std::cout << "Missing value for [t]" << std::endl;
				usage(), exit(1);
			}

			threshold = std::stof(argv[i+1]);
			i++;
		} else if (std::strcmp(argv[i], "-path") == 0 || std::strcmp(argv[i], "--path") == 0){
			if (i+1 >= argc) {
				std::cout << "Missing value for [path]" << std::endl;
				usage(), exit(1);
			}

			path = argv[i+1];
			i++;
		}

		i++;
	}

	if (k == -1){
		k = 9;
	}
	if (threshold == -1){
		threshold = 0.8;
	}
	if (path.empty()){
		usage(), exit(1);
	}
}

int main(int argc, char** argv){

	// std::ifstream infile(filename);

	int k;
	float threshold;
	std::string path;

	parseParams(argc-1, argv+1, k, threshold, path);

	std::cout << k << "\t" << threshold << "\t" << path << std::endl;

    return 0;
}