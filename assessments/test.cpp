#include <bits/stdc++.h>
using namespace std;

int main() {
	int T;
	cin >> T;
	while (T--) {
		int n, m, k;
		cin >> n >> m >> k;

		int L1 = n - m * k;
		int L2 = n / (m + 1);
		int L = min(L1, L2);

		vector<int> res;
		for (int rep = 0; rep < m + 1 && res.size() < n; ++rep) {
			for (int i = 0; i < L && res.size() < n; ++i) {
				res.push_back(i);
			}
		}

		for (int i = 0; i < n; ++i) {
			cout << res[i];
		}
        cout<<endl;
	}
	return 0;
}
