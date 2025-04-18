#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;
using ll = long long;

struct Roadwork {
    int start; 
    int end;   
    int x;     
};

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int N, Q;
    cin >> N >> Q;
    
    vector<Roadwork> events(N);
   
    vector<Roadwork> roadworks(N);
    for (int i = 0; i < N; i++){
        int S, T, X;
        cin >> S >> T >> X;
        int start = 2 * S - 2 * X - 1; 
        int end   = 2 * T - 2 * X - 1; 
        roadworks[i] = {start, end, X};
    }
    
   
    sort(roadworks.begin(), roadworks.end(), [](const Roadwork &a, const Roadwork &b) {
        return a.start < b.start;
    });
    
   
    vector<int> queries(Q);
    for (int i = 0; i < Q; i++){
        cin >> queries[i];
        queries[i] = 2 * queries[i]; 
    }
    
    using Pii = pair<int,int>;
    priority_queue<Pii, vector<Pii>, greater<Pii>> active;
    
    int idx = 0; 
    vector<int> ans(Q, -1);
    for (int i = 0; i < Q; i++){
        int d = queries[i];
        
        
        while (idx < N && roadworks[idx].start <= d) {
            active.push({roadworks[idx].x, roadworks[idx].end});
            idx++;
        }
        
        while (!active.empty() && active.top().second <= d) {
            active.pop();
        }
        
       
        if (!active.empty()) {
            ans[i] = active.top().first;
        } else {
            ans[i] = -1;
        }
    }
    
    
    for (int i = 0; i < Q; i++){
        cout << ans[i] << "\n";
    }
    
    return 0;
}
