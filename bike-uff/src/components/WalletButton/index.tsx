import { TouchableOpacity, Text, View, StyleSheet } from "react-native";
import { useWeb3Modal } from "@web3modal/wagmi-react-native";
import { styles } from "./styles";

import React, { useState } from 'react';
import { ethers } from 'ethers';

export const WalletButton = () => {
  // const { open } = useWeb3Modal(); 

  const [walletAddress, setWalletAddress] = useState('');
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const mnemonic = 'test test test test test test test test test test test junk';

  const connectWallet = async () => {
    console.log('Conectar carteira chamado');
    try {
      const provider = new ethers.providers.JsonRpcProvider('http://localhost:8545');
      const wallet = ethers.Wallet.fromMnemonic(mnemonic).connect(provider);
      setWalletAddress(wallet.address);
      setIsConnected(true);
      setError('');
      console.log('Carteira conectada:', wallet.address);
    } catch (error) {
        console.error('Erro ao conectar a carteira:', error);
        setError('Erro ao conectar a carteira.');
      }
  }

  const disconnectWallet = () => {
    setWalletAddress('');
    setIsConnected(false);
    setError('');
  };

  return (
    <View style={testStyles.container}>
      {isConnected ? (
        <TouchableOpacity style={styles.walletButton} onPress={disconnectWallet}>
          <Text style={styles.textButton}>Desconectar Carteira</Text>
        </TouchableOpacity>
      ) : (
        <TouchableOpacity style={styles.walletButton} onPress={connectWallet}>
          <Text style={styles.textButton}>Conectar Carteira</Text>
        </TouchableOpacity>
      )}
      {walletAddress ? (
        <Text style={testStyles.address}>Endereço da Carteira: {walletAddress}</Text>
      ) : null}
      {error ? (
        <Text style={testStyles.error}>{error}</Text>
      ) : null}
    </View>
  );
};

const testStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  walletButton: {
    backgroundColor: '#007bff',
    padding: 10,
    borderRadius: 5,
  },
  textButton: {
    color: '#fff',
    fontSize: 16,
  },
  address: {
    marginTop: 20,
    fontSize: 16,
  },
  error: {
    marginTop: 20,
    fontSize: 16,
    color: 'red',
  },
});



//   return (
//     <>
//       <TouchableOpacity style={styles.walletButton} onPress={() => open()}>
//         <Text style={styles.textButton}>Conecte-se com sua carteira</Text>
//       </TouchableOpacity>
//     </>
//   );
// };
