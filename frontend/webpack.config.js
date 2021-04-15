module.exports = {
  module: {
    rules: [
      {
        test: /\.(jsx|js)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.css$/,
        //order is important here. css-loader creates javascript from css and the style loader injects the javascript into the dom
        //js from css must first be generated and the style must then be injected.
        //however, the order is reversed in the array so order is "style-loader", "css-loader"
        use: ["style-loader", "css-loader"]
      }
    ]
  }
};