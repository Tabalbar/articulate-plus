// const PCA = require('pca-js')
const {PCA} = require('ml-pca')

module.exports = (data) => {
    Array.prototype.contains = (v) => {
        for (var i = 0; i < this.length; i++) {
            if (this[i] === v) return true;
        }
        return false;
    };

    Array.prototype.unique = () => {
        var arr = [];
        for (var i = 0; i < this.length; i++) {
            if (!arr.contains(this[i])) {
                arr.push(this[i]);
            }
        }
        return arr;
    }


    // var duplicates = [1, 3, 4, 2, 1, 2, 3, 8];
    // var uniques = duplicates.unique(); // result = [1,3,4,2,8]
    let keys = Object.keys(data[0])
    let nominalKeys = []
    for (let i = 0; i < keys.length; i++) {
        if (isNaN(data[0][keys[i]]) && keys[i] !== 'tableData') {
            nominalKeys.push(keys[i])
        }
    }
    // let PCAData = []
    // for (let i = 0; i < nominalKeys.length; i++) {
    //     let tmpData = []
    //     for (let j = 0; j < data.length; j++) {
    //         tmpData.push()
    //     }
    //     let uniques = PCAData.unique()
    //     console.log(uniques)
    // }

    let testPCAData = []

    for(let i = 0; i < data.length; i++) {
        testPCAData.push([data[i]['math score'], data[i]['writing score'], data[i]['reading score'] ])
    }
    const pca = new PCA(testPCAData)
    // console.log(testPCAData)
    console.log(pca.getLoadings());

    // let vectors = PCA.getEigenVectors(testPCAData)
    // const first = PCA.computePercentageExplained(vectors, vectors[0])
    // console.log(first)
    // let tmp1 = []
    // let tmp2 = []
    // for( let i = 0; i < data.length; i++) {
    //     tmp1.push(data[i]['math score'])
    //     tmp2.push(data[i]['writing score'])
    // }
    // // console.log(covariance(tmp1, tmp2, tmp1.length))
    // console.log(covariance(tmp1, tmp2, tmp1.length))

}

// function mean(arr, n) {
//     let sum = 0;
//     for(let i = 0; i < n; i++) {
//         sum += parseInt(arr[i])
//     }
//     return (sum / n)
// }

// function covariance(arr1, arr2, n) {
//     let sum = 0;
//     for(let i = 0; i < n; i++) {
//         sum = sum + (parseInt(arr1[i]) - mean(arr1, n)) * (parseInt(arr2[i]) - mean(arr2, n));
//     }
//     return sum/(arr1.length - 1)
// }